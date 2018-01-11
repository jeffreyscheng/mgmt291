pip freeze > requirements2.txt
sort requirements.txt requirements2.txt | uniq > requirements.txt
rm requirements2.txt
