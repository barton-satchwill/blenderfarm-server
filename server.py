#!flask/bin/python

from flask import Flask,jsonify,abort,request
import os, shutil, time
from threading import Thread

app = Flask(__name__)

logfile = 'render.log'
blender = '/home/ubuntu/blender-2.73/blender'
output_root = '/home/ubuntu/images'
blend_root = '/home/ubuntu/blend'


@app.route('/set_repo', methods=['POST', 'GET'])
def set_repo():
	blend_dir = '/home/ubuntu/blend'
	if os.path.isdir(blend_dir):
		shutil.rmtree(blend_dir)
	cmd = 'git clone %s %s' % (request.args.get('url'), blend_dir)
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
	return print_args(request.args)


@app.route('/render_status', methods=['POST','GET'])
def render_status():
	return print_args(request.args)


app.route('/')
def index():
	return "Hi, Bart!\n"



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


def store():
	print "uploading to Swift..."





if __name__ == '__main__':
	#app.run(debug=True)
	#app.run(host='0.0.0.0', port=port, debug=True)
	app.run(host='::', debug=True)
