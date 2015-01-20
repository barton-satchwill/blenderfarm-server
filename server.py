#!flask/bin/python

from flask import Flask,jsonify,abort,request
import os
import shutil

app = Flask(__name__)

@app.route('/set_repo', methods=['POST', 'GET'])
def set_repo():
	
	print("checking for dir")
	print os.path.isdir('/home/ubuntu/iae-sub')
	if os.path.isdir('/home/ubuntu/iae-sub'):
		print("yep, found it.  will delete...")
		shutil.rmtree('/home/ubuntu/iae-sub')
	cmd = 'git clone https://<username>:<password>"@%s ~/iae-sub' % (request.args.get('url'))
	print cmd
	os.system(cmd)
	return "I'm going to set the repo to '" + request.args.get('url') + "'."


@app.route('/')
def index():
	return "This is a BlenderFarm API server.\n"



if __name__ == '__main__':
	#app.run(debug=True)
	#app.run(host='0.0.0.0', port=port, debug=True)
	app.run(host='::', debug=True)



