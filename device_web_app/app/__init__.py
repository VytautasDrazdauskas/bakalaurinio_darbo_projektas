import BaseHTTPServer
import cgi
import os
import controllers

DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIR)

def get_form_value(item_list, key):
        for item in item_list:
            if (item.name == key):
                return item.value
        return None

class Handler( BaseHTTPServer.BaseHTTPRequestHandler ):

    def do_GET( self ):
        self.send_response(200)

        #CSS uzkrovimas
        if (self.path == "/style.css"):
            self.send_header( 'Content-type', 'text/css' )
            self.end_headers()
            self.wfile.write( open('static/style/style.css').read())
            return

        self.send_header( 'Content-type', 'text/html' )
        self.end_headers()

        if (self.path == "/index" or self.path == "/"):
            self.wfile.write( open('views/index.htm').read())            
        elif (self.path == "/mesh"):
            mesh_id = '1' #controllers.load_mesh_id()
            password = '1' #controllers.load_key()
            mesh_fwding = '1' #controllers.load_mesh_fwding()
            self.wfile.write( open('views/mesh.htm').read().format(mesh_id=mesh_id, password=password, mesh_fwding=mesh_fwding))
        elif (self.path == "/reboot-wifi"):
            controllers.reboot_wifi()
            self.wfile.write( open('views/success.htm').read())
        elif (self.path == "/success"):
            self.wfile.write( open('views/success.htm').read())
        else:
            self.wfile.write( open('views/error.htm').read())

    def do_POST(self):
        self.send_response(200)
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        if ('/mesh_save' == self.path):
            mesh_id = get_form_value(form.list, "meshId")
            password = get_form_value(form.list, "password")
            mesh_fwding = get_form_value(form.list, "meshFwding")
            controllers.save_config(mesh_id=mesh_id, password=password, mesh_fwding=mesh_fwding)
            self.send_header('Location','/success')
            self.end_headers()

httpd = BaseHTTPServer.HTTPServer( ('0.0.0.0', 8080), Handler )
print("Startuojamas serveris.")
httpd.serve_forever()