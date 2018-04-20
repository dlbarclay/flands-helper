src:	mainwindow.ui flandshelper.py tickbox64.png 
	zip -r flandshelper.zip mainwindow.ui flandshelper.py tickbox64.png 

clean:	
	rm -r __pycache__/ build/ dist/ 
	
