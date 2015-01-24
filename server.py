#!flask/bin/python

import sys, os, shutil, time
import subprocess, shlex
from flask import Flask,jsonify,abort,request
from threading import Thread
sys.path.append("/usr/lib/python2.7/dist-packages")
import swiftclient

app = Flask(__name__)

root = '/home/ubuntu'
logfile = 'render.log'
bucket = 'mybucket'
blender = 'blender'
output_root = os.path.join(root, 'images')
blend_root = os.path.join(root, 'blend')
config_file = os.path.join(root, 'openrc')

@app.route('/set_repo', methods=['POST', 'GET'])
def set_repo():
	if os.path.isdir(blend_root):
		shutil.rmtree(blend_root)
	cmd = 'git clone %s %s' % (request.args.get('url'), blend_root)
	os.system(cmd)
	return ""



@app.route('/render_start', methods=['POST','GET'])
def render_start():
	blend = os.path.join(blend_root, request.args.get('blend'))
	output_dir = os.path.join(output_root,request.args.get('output_dir')+"#####")
	start_frame = request.args.get('start_frame')
	end_frame = request.args.get('end_frame')
	if start_frame and end_frame:
		start_frame = "--frame-start " + start_frame
		end_frame = "--frame-end " + end_frame

	t1 = Thread(target=render, args=(blender, blend, output_dir, start_frame, end_frame, logfile))
	t1.start()
	return ''



@app.route('/render_stop', methods=['POST','GET'])
def render_stop():
	return subprocess.check_output(['pkill','blender'])



@app.route('/render_status', methods=['POST','GET'])
def render_status():
	hostname = subprocess.check_output('hostname')[:-1]
	render_status = '================= ' + hostname + ' ====================\n'
	cmd = shlex.split('grep -E "Starting|Saved" %s' % (logfile))
	p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	for item in p.communicate():
		render_status = render_status + item 

	cmd = shlex.split('tail %s' % (logfile))
	p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

	for item in p.communicate():
		render_status = render_status + item

	return render_status



app.route('/')
def index():
	return "Hi, Bart!\n"


# ==================================================================================

def print_args(args):
	arg_list = []
	for arg in args:
		arg_list.append(arg)
	return "returning " + ", ".join(arg_list)



def render(blender, blend, output_dir, start_frame, end_frame, logfile):
	cmd = '%s -noaudio --background %s --render-output %s %s %s --render-anim --render-format PNG >> %s' % (blender, blend, output_dir, start_frame, end_frame, logfile)
	now = time.strftime("%c")
	f = open(logfile, 'a')
	f.write("---------------------- Starting %s render at %s ----------------------\n" % (blend, now))
	f.write("%s\n" % cmd)
	f.write("--------------------------------------------------------------------------\n")
	f.flush()
	f.close
	os.system(cmd)
	store()
	swift_status()



def swift_status():
	root = '/home/ubuntu'
	bucket = 'mybucket'

	print "reporting on Swift..."
	swift = swiftclient.Connection(
	authurl=os.environ['OS_AUTH_URL'], key=os.environ['OS_PASSWORD'],
	user=os.environ['OS_USERNAME'], tenant_name=os.environ['OS_TENANT_NAME'],
	auth_version=2)

	print "----------------"
	for container in swift.get_account()[1]:
		#if bucket is container['name']:
		if True:
			print container['name']
			for data in swift.get_container(container['name'])[1]:
				print '{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])
			print "----------------"



def store():
	print "uploading to Swift..."
	swift = swiftclient.Connection(
		authurl=os.environ['OS_AUTH_URL'],
		key=os.environ['OS_PASSWORD'],
		user=os.environ['OS_USERNAME'],
		tenant_name=os.environ['OS_TENANT_NAME'],
		auth_version=2)

	swift.put_container(bucket)
	for dirname, subdirs, filenames in os.walk(os.path.join(root, 'images')):
		for filename in filenames:
			f = os.path.join(dirname, filename).replace(root, '').lstrip('/')
			swift.put_object(bucket, f, open(f,'r'))


def config():
	cmd = ['bash', '-c', 'cat %s' % config_file]
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
	for line in proc.stdout:
		line = line.replace('export ', '').replace('"', '').strip()
		(key, _, value) = line.partition("=")
		os.environ[key] = value
	proc.communicate()



if __name__ == '__main__':
	config()
	app.run(host='::', debug=True)

