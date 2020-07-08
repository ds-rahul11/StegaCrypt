from flask import Flask, render_template, url_for, request
from PIL import Image
import os

app = Flask(__name__)

'''encryption starts here'''
def encrypt(key, msg):
    encryped = []
    for i, c in enumerate(msg):
        key_c = ord(key[i % len(key)])
        msg_c = ord(c)
        encryped.append(chr((msg_c + key_c) % 127))
    return ''.join(encryped)
def genData(data): 
		
	# list of binary codes 
	# of given data 
	newd = [] 
		
	for i in data: 
		newd.append(format(ord(i), '08b')) 
	return newd

def modPix(pix, data): 
	datalist = genData(data) 
	lendata = len(datalist) 
	imdata = iter(pix) 

	for i in range(lendata): 
		
		# Extracting 3 pixels at a time 
		pix = [value for value in imdata.__next__()[:3] + imdata.__next__()[:3] + imdata.__next__()[:3]] 
									
		# Pixel value should be made 
		# odd for 1 and even for 0 
		for j in range(0, 8): 
			if (datalist[i][j]=='0') and (pix[j]% 2 != 0): 
				
				if (pix[j]% 2 != 0): 
					pix[j] -= 1
					
			elif (datalist[i][j] == '1') and (pix[j] % 2 == 0): 
				pix[j] -= 1
				
		# Eigh^th pixel of every set tells 
		# whether to stop ot read further. 
		# 0 means keep reading; 1 means the 
		# message is over. 
		if (i == lendata - 1): 
			if (pix[-1] % 2 == 0): 
				pix[-1] -= 1
		else: 
			if (pix[-1] % 2 != 0): 
				pix[-1] -= 1

		pix = tuple(pix) 
		yield pix[0:3] 
		yield pix[3:6] 
		yield pix[6:9]

def encode_enc(newimg, data): 
	w = newimg.size[0] 
	(x, y) = (0, 0) 
	
	for pixel in modPix(newimg.getdata(), data): 
		
		# Putting modified pixels in the new image 
		newimg.putpixel((x, y), pixel) 
		if (x == w - 1): 
			x = 0
			y += 1
		else: 
			x += 1
			
# Encode data into image 
def encode(encrypted,image): 
	
	
	data = encrypted 
	if (len(data) == 0): 
		raise ValueError('Data is empty') 
		
	newimg = image.copy() 
	encode_enc(newimg, data)
	UPLOAD_FOLDER = 'static'
	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
	newimg.save(os.path.join(app.config['UPLOAD_FOLDER'], "encoded_img.png"))
	
'''encryption process ends here'''

'''decryption code start here'''
def decrypt(key, encryped):
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)
def decode(image): 
	
	data = '' 
	imgdata = iter(image.getdata()) 
	
	while (True): 
		pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]] 
		# string of binary data 
		binstr = '' 
		
		for i in pixels[:8]: 
			if (i % 2 == 0): 
				binstr += '0'
			else: 
				binstr += '1'
				
		data += chr(int(binstr, 2)) 
		if (pixels[-1] % 2 != 0): 
			return data
'''Decryption ends here'''

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/how_to_use')
def howto():
    return render_template('how_to_use.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/encryption')
def enc():
    return render_template('encrypt.html')
@app.route('/en_complete', methods=['GET', 'POST'])
def en_complete():
    if request.method=='GET':
        return render_template('encrypt_comp.html')
    if request.method=='POST':    

        filename = request.files['file']
        key_received = request.form['Key']
        image = Image.open(filename, 'r')
        msg_received = request.form['content']
        if key_received == "":
            key_received = 'msritcodes'
        encrypted_msg = encrypt(key_received, msg_received)
        encode(encrypted_msg,image)
        new_img = "encoded_img.png"
        return render_template('encrypt_comp.html', msg = msg_received , key = encrypted_msg, image_name = new_img)
@app.route('/decryption')
def dec():
    return render_template('decrypt.html')
@app.route('/de_complete', methods=['GET', 'POST'])
def de_complete():
    if request.method=='GET':
        return render_template('encrypt_comp.html')
    if request.method=='POST':    
        filename = request.files['file']
        key_received = request.form['Key']
        image = Image.open(filename, 'r')
        if key_received == "":
            key_received = 'msritcodes'
        received_msg = decode(image)
        msg = decrypt(key_received, received_msg)
        return render_template('decrypt_comp.html', dec_msg = msg)	


if __name__ == '__main__':
   app.run()
