from http.server import BaseHTTPRequestHandler, HTTPServer

fruits = {
    'schema':{
        'name':{
            'type':'string'
        },'color':{
            'type':'string'
        },'size':{
            'type':'integer'
        }
    },
    'data':
    [
        {'name':'apple','color':'red', 'size':2},
        {'name':'peach','color':'orange', 'size':1}
    ]
}

class HungryHippoServer(BaseHTTPRequestHandler):

    def __init__(self, *args):
        self.validstores = {'fruits':fruits}
        BaseHTTPRequestHandler.__init__(self, *args)

    def setupPathSplit(self):
        path_spl = self.path.split("/")
        if(path_spl[0]==''):
            path_spl.pop(0)
        return path_spl

    def do_GET(self):
        reqdetails = self.parseURLPath()
        json_str = ''
        """For GET requests, default to the fruits store if no store provided."""
        if(reqdetails['store']==None):
            reqdetails['store'] = 'fruits'
        """Check if the requested store is a valid store."""
        if(reqdetails['store'] in self.validstores.keys()):
            if(reqdetails['item']==None):
                """Return all fruits from the fruit store."""
                self.setup200resp()
                json_str = str(self.validstores[reqdetails['store']]['data'])
            else:
                storeres = [item for item in self.validstores[reqdetails['store']]['data'] if item['name']==reqdetails['item']]
                if(len(storeres)==0):
                    """return empty data if no store exists"""
                    self.setup200resp()
                    json_str = str({"warn": "No entry for " + reqdetails['item'] + " in " + reqdetails['store']})
                elif(len(storeres)==1):
                    """Get the specified fruit from the fruit store."""
                    self.setup200resp()
                    json_str = str(storeres[0])
                else:
                    self.setup400resp()
                    json_str = str({"error": "Multiple entries for " + reqdetails['item'] + " in " + reqdetails['store'] + ". Likely a corrupt store.  Fix data manually."})
        else:
            self.setup400resp()
            json_str = str({"error": reqdetails['store'] + " is not a valid store."})

        """Send the JSON string to the HTTP file writer."""        
        output = json_str.encode()
        self.wfile.write(output)
        return

    def do_POST(self):
        reqdetails = self.parseURLPath()
        json_str = ''
        if(reqdetails['store']==None):
            self.setup400resp()
            json_str = str({"error": "No store specified for update."})
        elif(reqdetails['item']==None):
            self.setup400resp()
            json_str = str({"error": "No item in " + reqdetails['store'] + " specified for update."})
        elif(reqdetails['store'] in self.validstores.keys()):
           storeres = [item for item in self.validstores[reqdetails['store']]['data'] if item['name']==reqdetails['item']]
           if(len(storeres)==1):
               try:
                    rdata = str(self.rfile.read(int(self.headers['Content-Length'])), 'utf-8')
                    rdict = dict(param.split("=") for param in rdata.split("&"))
                    storeschema = self.validstores[reqdetails['store']]['schema']
                    for k in rdict.keys():
                        if(storeschema[k]['type']=='integer'):
                            storeres[0][k] = int(rdict[k])
                        else:
                            storeres[0][k] = rdict[k]
                    rdict['name'] = storeres[0]['name']
                    rdict['success'] = True
                    json_str = str(rdict)
                    self.setup200resp()
               except(ValueError):
                    self.setup400resp()
                    json_str = str({"error": "Parsing exception, likely from str to int."})
           elif(len(storeres)==0):
               self.setup400resp()
               json_str = str({"error": reqdetails['item'] + " in " + reqdetails['store'] + " does not exist.  Please add it to the store using PUT."})  
           else:
               self.setup400resp()
               json_str = str({"error": reqdetails['item'] + " in " + reqdetails['store'] + " has multiple entries.  Likely a corrupt store.  Fix manually."})                  
        else:
            self.setup400resp()
            json_str = str({"error": reqdetails['store'] + " is not a valid store."})          


        """Send the JSON string to the HTTP file writer."""        
        output = json_str.encode()
        print(fruits)
        self.wfile.write(output)
        return

    def setup200resp(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def setup400resp(self):
        self.send_response(400)
        self.send_header('Content-type','application/json')
        self.end_headers()

    def parseURLPath(self):
        path_spl = self.setupPathSplit()
        reqdetails = {}
        if(len(path_spl)==0 or path_spl[0]==''):
            reqdetails['store'] = None
            reqdetails['item'] = None
        elif(len(path_spl)==1 or path_spl[1]==''):
            reqdetails['store'] = path_spl[0]
            reqdetails['item'] = None
        else:
            reqdetails['store'] = path_spl[0]
            reqdetails['item'] = path_spl[1]
        return reqdetails
        

if(__name__=="__main__"):
    try:
        server = HTTPServer(('',8626), HungryHippoServer)
        print("Starting server on port 8626")
        server.serve_forever()
    except(KeyboardInterrupt):
        print("Keyboard Interrupt Recv'd")
        server.socket.close()
        