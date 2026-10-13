import sys, os, io, json, tempfile, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
import app.database as dbm
tmp=pathlib.Path(tempfile.mkdtemp())/'t.db'
dbm.DATABASE=tmp
import app.web as web
c=web.app.test_client()
res=[]
def check(name,cond): res.append((name,bool(cond))); print(('PASS' if cond else 'FAIL'),name)

r=c.get('/home'); check('Dashboard blocked when logged out (redirect to login)', r.status_code==302 and '/login' in r.headers['Location'])
r=c.post('/register',data={'full_name':'Test Student','email':'t@example.com','password':'pass123','confirm_password':'other'})
check('Registration rejects mismatched passwords', b'do not match' in r.data)
r=c.post('/register',data={'full_name':'Test Student','email':'t@example.com','password':'pass123','confirm_password':'pass123'})
check('Registration succeeds and opens dashboard', r.status_code==302 and '/home' in r.headers['Location'])
c.get('/logout')
r=c.post('/register',data={'full_name':'X','email':'t@example.com','password':'a','confirm_password':'a'})
check('Duplicate email rejected', b'already exists' in r.data)
r=c.post('/login',data={'email':'t@example.com','password':'wrong'})
check('Login rejects wrong password', b'Invalid email or password' in r.data)
r=c.post('/login',data={'email':'t@example.com','password':'pass123'})
check('Login accepts valid credentials', r.status_code==302 and '/home' in r.headers['Location'])
conn=dbm.get_connection(); pw=conn.execute('select password from users').fetchone()[0]; conn.close()
check('Password stored as hash (not plain text)', pw!='pass123' and pw.startswith(('scrypt','pbkdf2')))
for path in ('/home','/materials','/timetable'):
    check(f'Page {path} loads when logged in', c.get(path).status_code==200)
r=c.get('/home'); check('Dashboard shows no activities before a timetable exists', b'No upcoming activities' in r.data)

# timetable save -> dashboard
sched=[{'day':d,'available':True,'sessions':[
  {'module':'Mathematics','assessment':'Exam','start':1080,'end':1140,'duration':60},
  {'break':True,'start':1140,'end':1155},
  {'module':'Physics','assessment':'Test','start':1155,'end':1215,'duration':60}]} for d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']]
r=c.post('/save-timetable',json={'schedule':sched})
check('Timetable saved to database (breaks excluded)', r.status_code==200 and r.get_json()['saved']==14)
r=c.get('/home')
check('Dashboard now lists upcoming activities from saved timetable', b'Mathematics' in r.data and b'No upcoming activities' not in r.data)
r=c.post('/save-timetable',json={'schedule':sched[:1]})
check('Saving again replaces the old timetable', len(dbm.get_timetable(1))==2)
r=c.post('/save-timetable',json={'schedule':'bad'})
check('Invalid timetable data rejected', r.status_code==400)
c2=web.app.test_client(); r=c2.post('/save-timetable',json={'schedule':sched})
check('Saving timetable requires login', r.status_code==401)

# uploads
def make_pdf(lines):
    stream="BT /F1 11 Tf 40 780 Td 14 TL "+" ".join("("+l+") Tj T*" for l in lines)+" ET"
    objs=["<< /Type /Catalog /Pages 2 0 R >>","<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
          "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
          "<< /Length %d >>\nstream\n%s\nendstream"%(len(stream),stream),"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out="%PDF-1.4\n"; offs=[]
    for i,o in enumerate(objs,1):
        offs.append(len(out)); out+="%d 0 obj\n%s\nendobj\n"%(i,o)
    x=len(out); out+="xref\n0 %d\n0000000000 65535 f \n"%(len(objs)+1)
    for o in offs: out+="%010d 00000 n \n"%o
    out+="trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF"%(len(objs)+1,x)
    return out.encode()
pdfbytes=make_pdf(["Photosynthesis is the process by which plants convert light into chemical energy.",
 "An important example is the Calvin cycle, which fixes carbon dioxide into sugars.",
 "Therefore chlorophyll absorbs light mainly in the blue and red wavelengths of the spectrum."])
r=c.post('/upload',data={'module_name':'Biology','notes_file':(io.BytesIO(b'hello'),'notes.txt')},content_type='multipart/form-data')
check('Upload rejects non-PDF file', b'Only PDF' in r.data)
r=c.post('/upload',data={'module_name':'Biology'},content_type='multipart/form-data')
check('Upload with no file shows message', b'select at least one PDF' in r.data)
r=c.post('/upload',data={'module_name':'Biology','notes_file':(io.BytesIO(pdfbytes),'notes.pdf'),'scope_file':(io.BytesIO(pdfbytes),'scope.pdf')},content_type='multipart/form-data')
check('Valid PDFs uploaded, text extracted and analysed', r.status_code==200 and b'Biology_notes.pdf' in r.data and b'Study Analysis' in r.data and b'Photosynthesis' in r.data)
check('Files saved into scope and notes folders', (web.SCOPE_FOLDER/'Biology_scope.pdf').exists() and (web.NOTES_FOLDER/'Biology_notes.pdf').exists())
print(sum(p for _,p in res),'/',len(res))
for f in (web.SCOPE_FOLDER/'Biology_scope.pdf',web.NOTES_FOLDER/'Biology_notes.pdf'):
    f.unlink()
