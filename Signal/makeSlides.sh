#!/bin/bash
EXT=$1
pwd0=$PWD
cd $EXT/sigfit
pwd1=$PWD
ls *interp.pdf > tmp.txt
sed -i -e "s/_interp.pdf//g" tmp.txt 
#cat tmp.txt

mkdir -p $pwd0/$EXT/sigfit/slides
cp $pwd0/tex/Intro.tex $pwd0/$EXT/sigfit/slides/.
cp $pwd0/tex/Outro.tex $pwd0/$EXT/sigfit/slides/.

while read p
do
echo "Making slide for $p"
cp $pwd0/tex/slide.tex $pwd0/$EXT/sigfit/slides/slide_${p}.tex
sed -i -e "s/!NAMEEXT!/$EXT/g" $pwd0/$EXT/sigfit/slides/slide_${p}.tex
sed -i -e "s/!NAME!/$p/g" $pwd0/$EXT/sigfit/slides/slide_${p}.tex
q=${p/_/ }
r=${q/_/ }
sed -i -e "s/!TITLE!/$r/g" $pwd0/$EXT/sigfit/slides/slide_${p}.tex

done < tmp.txt

echo "cat  $pwd0/$EXT/sigfit/slides/Intro.tex $pwd0/$EXT/sigfit/slides/slide*{ggh,vbf,tth,wh,zh}*tex  $pwd0/$EXT/sigfit/slides/Outro.tex > $pwd0/$EXT/sigfit/slides/fullslides.tex"
cat  $pwd0/$EXT/sigfit/slides/Intro.tex $pwd0/$EXT/sigfit/slides/slide*{ggh,vbf,tth,wh,zh}*tex  $pwd0/$EXT/sigfit/slides/Outro.tex > $pwd0/$EXT/sigfit/slides/fullslides.tex


cd -
pdflatex -interaction nonstopmode $pwd0/$EXT/sigfit/slides/fullslides.tex 
#sed -i -e "s/\!EXT\!/$EXT/g" combineHarvesterOptions13TeV_$EXT.datt
