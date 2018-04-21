default:	flandshelper.py
	./pyinstall.sh

src:	mainwindow.ui flandshelper.py tickbox64.png 
	zip -r flandshelper.zip mainwindow.ui flandshelper.py tickbox.ico 

clean:	
	rm -rf __pycache__/ build/ dist/ flandshelper.spec model.json model.json.backup
	
