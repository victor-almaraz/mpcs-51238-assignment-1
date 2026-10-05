import socket, json, sys, base64, time
class M:
    def __init__(s, port=2828):
        s.s=socket.create_connection(('localhost',port)); s.id=0; s.read()
    def read(s):
        buf=b''
        while b':' not in buf: buf+=s.s.recv(1)
        n,rest=buf.split(b':',1); n=int(n)
        while len(rest)<n: rest+=s.s.recv(n-len(rest))
        return json.loads(rest)
    def cmd(s,name,params=None):
        s.id+=1; msg=json.dumps([0,s.id,name,params or {}]).encode()
        s.s.sendall(str(len(msg)).encode()+b':'+msg)
        r=s.read()
        if r[2]: raise Exception(json.dumps(r[2])[:2000])
        return r[3]
m=M()
m.cmd('WebDriver:NewSession',{'capabilities':{}})
def js(src, args=None, asyn=False):
    return m.cmd('WebDriver:ExecuteAsyncScript' if asyn else 'WebDriver:ExecuteScript',{'script':src,'args':args or [], 'scriptTimeout':60000})['value']
def shot(path):
    v=m.cmd('WebDriver:TakeScreenshot',{})['value']; open(path,'wb').write(base64.b64decode(v))
