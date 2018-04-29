default:	flandshelper.py
	./pyinstall.sh

clean:	
	rm -rf __pycache__/ build/ dist/ flandshelper.spec model.json model.json.backup
	
