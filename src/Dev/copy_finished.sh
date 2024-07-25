ls *out.cell > finished.txt
cat finished.txt | rev | cut -c 10- | rev | awk '{print $1".res"}' > finished.txt
cat finished.txt | while read x ; do cp $x ../LaRu4Bi12/all/ ; done

