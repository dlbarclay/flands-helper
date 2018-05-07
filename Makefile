default:	flandshelper.py
	./pyinstall.sh

mainwindow:	res/mainwindow.ui
	python3 -m PyQt5.uic.pyuic -x res/mainwindow.ui -o mainwindow.py

clean:	
	rm -rf __pycache__/ build/ dist/ flandshelper.spec model.json model.json.backup mainwindow.py
	
