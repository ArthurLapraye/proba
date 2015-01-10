#!/usr/bin/python 
# -*- coding: utf-8 -*-

#Implémentation de l'algorithme de Viterbi - TP3 - Arthur Lapraye - 2014

import re
import sys
import random
import numpy as np
import functools as funk
from optparse import OptionParser

usage=u"""
	./Lapraye-tp3.py [options] corpus
	  Ce programme implémente l'algorithme de Viterbi pour l'étiquetage morpho-syntaxique, 
	  ainsi que d'autres algorithmes plus simplistes afin d'en comparer les performances. 
	  Il opère sur un corpus dont 90% est utilisé pour la création de matrices de transitions
	  et d'émission, et 10% est utilisé pour tester les algorithmes. 
	  """

p = OptionParser(usage=usage)
p.add_option("-m", "--matrice",
                  action="store_true", dest="matrice", default=False,
                  help=u"Cette option permet d'afficher les matrices de confusions pour chaque algorithme et de les comparer de façon plus fine.")

p.add_option("-a", "--absolute-values",
                  action="store_false", dest="percent", default=True,
                  help=u"Cette option permet de remplacer les pourcentages affichés par défaut par des valeurs absolues.")
                  
(op,args)=p.parse_args()

#Variables globales
TEST=9 
MATRICE=op.matrice
PERCENT=op.percent
LISSAGE= np.log2(10**-10)

#Fonction de lecture du fichier
def liredonnees(filename):

	tabz=re.compile("\t") #Expression régulière pour couper les lignes du fichier
	test=[] #Corpus de test
	sentence=[] #Liste de tuples mots/catégorie utilisée pour construire le corpus de test
	
	wordcounts = {} #comptage de mots 
	prevcounts = {} #comptage de catégories
	matrem = {} #distribution d'émission
	matran = {} #distribution de transition
	
	#filesize=os.path.getsize(filename)
	#trb = 0
	
	cats=set() #Ensemble des catégories
	
	prevcat = "S"	#Séparateur de phrases
	
	c=random.randint(0,TEST)
	# "Return a random integer N such that a <= N <= b."
	#Tirage au sort pour déterminer si une phrase donnée rejoint le corpus de test 
	#Ou si elle est utilisée pour l'apprentissage

	with open(filename) as treebank:
		treebank.readline() #Élimine la première ligne
		for line in treebank:
		
			[word, _, cat, subcat, _, _ , _ , _ , _] = tabz.split(line)
			
			word=word.lower()
			cats.add(cat)
			
			if c == TEST:
				sentence.append((word, cat))
				#Si la phrase courante fait partie du corpus de test
				#Il faut lui rajouter le mot courant
			else:
				#Si la phrase courante fait partie du corpus d'entraînement.
				
				#Comptage des catégories 
				if prevcat in prevcounts:
					prevcounts[prevcat] += 1.0
				else:
					prevcounts[prevcat] = 1.0
				
				#Comptage des mots
				if word in wordcounts:
					wordcounts[word] += 1.0
				else:
					wordcounts[word] = 1.0
				
			
				#Matrice de transition : comptage des transitions de prevcat à cat
				if (prevcat,cat) in matran:
					matran[prevcat,cat] += 1.0
				else:
					matran[prevcat,cat] = 1.0
			
				#Matrice d'émission : comptage des émissions d'un mot pour une catégorie donnée.
				if (cat,word) in matrem:
					matrem[cat,word] += 1.0
				else:
					matrem[cat,word] =1.0
			
			if subcat  == "s" and "PONCT" == cat:
				#Si la sous-catégorie du token courant est "s", c'est un séparateur de phrase.
				
				if  c == TEST: 
					test += [sentence]
					#Si la phrase fait partie du corpus de test, il faut l'y rajouter.
				else:	
					#Sinon, il faut incrémenter le nombre de transitions entre la catégorie actuelle
					#Et une fin de phrase.
					if (cat,"S") in matran:
						matran[cat,"S"] += 1.0
					else:
						matran[cat,"S"] = 1.0
				
					if cat in prevcounts:
						prevcounts[cat] += 1.0
					else:
						prevcounts[cat] = 1.0
			
				prevcat = "S"	
				sentence= []
				c = random.randint(0,TEST)
			else:
				#Si l'élément courant n'est pas un séparateur de phrase
				#Il faut simplement garder en mémoire la catégorie actuelle
				#pour le décompte des transitions.
				prevcat = cat
	
	#Une fois le comptage des données terminés
	#Les comptes sont convertis en log probabilités.
	
	for c in matran:
		p,q=c
		matran[c]=np.log2(matran[c]/prevcounts[p])

	for c in matrem:
		p,q=c
		matrem[c]=np.log2(matrem[c]/prevcounts[p])
	
	return (test,matran,matrem,prevcounts,wordcounts,cats)

#Algorithme étiquetant au hasard :-]  
def randchoice(sentence):
	return [random.choice(list(cats)) for a in sentence]

#Algorithme d'étiquette de catégorie majoritaire :
#La fonction déduit l'étiquette majoritaire à partir du compte des catégories, et renvoie une fonction, majo,
#attribuant systématiquement l'étiquette majoritaire à tous les mots de la phrase.
def majoritywins(prevcounts):
	u=0
	for p in prevcounts:
		z=prevcounts[p]
		if z > u:
			u=z
			commonest=p
	
	def majo(sentence):
		return [commonest for a in sentence]
	
	return majo

#Cette fonction déduit une étiquette à partir de la meilleure probabilité contenue dans la matrice d'émission
#pour un mot. 
def baseline2(sentence):
	if len(sentence) == 0:
		return []
	else:
		p,_=sentence[0]
		z= -np.Inf
		bestcat="N"
		
		for cat in cats:
			s=matrem.get((cat,p) ,LISSAGE)
			if s > z:
				z=s
				bestcat=cat
		return [bestcat] + baseline2(sentence[1:])

#Cette fonction déduit la catégorie d'un mot à partir de la probabilité conjointe de son émission et de la transition depuis
#la catégorie précédente.
#Elle revient à choisir le chemin localement optimal dans le treillis de Viterbi, sans mémoire des états précédents
def naive(prev,sentence):
	if len(sentence) == 0:
		return []
	else:
		p,_=sentence[0]
		p=p.lower()
		z=-np.Inf
		bestcat="N"
	
		for cat in cats:
			s = matrem.get((cat,p), LISSAGE) + matran.get((prev,cat),LISSAGE)
			if s > z:
				z=s
				bestcat=cat
	
		return [bestcat] + naive(bestcat,sentence[1:])

#Application partielle de la fonction, lui permettant d'évaluer les probabilités de transition d'un séparateur de phrase
#vers le premier mot
nv=funk.partial(naive,"S")

#Algorithme de Viterbi
def viterbi(sentence):
	pointeurs = []
	viterbo = []

	previt = {}
	back1 = {}
	
	w,_=sentence[0]
	
	#Calcul de la meilleure probabilité pour le début de phrase = probabilité d'émission pour chaque catégorie + probabilité de transition
	#depuis un début de phrase
	for cat in cats:
		previt[cat] = matrem.get((cat,w),LISSAGE) + matran.get(("S",cat), LISSAGE)
		back1[cat] = "S"
	
	
	pointeurs.append(back1)
	for (w,_) in sentence[1:]:
		vitn = {}
		backn={}
		
		for cat in cats:
			bestprob = -np.Inf
			bestag = ""
			probem = matrem.get((cat,w),LISSAGE)
			
			for tag in cats:
				z= previt[tag] + probem + matran.get((tag,cat),LISSAGE)
				if z > bestprob:
					bestprob=z
					bestag=tag
			
			#Calcul de la meilleure probabilité pour chaque conjonction mot-étiquette-étiquette précédente
		
			vitn[cat] = bestprob
			backn[cat] = bestag
		
		pointeurs.append(backn)
		previt = vitn 
	
	bestprob = -np.Inf
	bestag = ""
	lastword=sentence[-1][0]
	
	#Calcul de la meilleure probabilité pour le dernier mot de la phrase.
	for tag in cats:
		z= previt[tag] + matran.get((tag,"S"),LISSAGE) #+ matrem.get((tag,lastword),LISSAGE)
		if z > bestprob:
			bestprob=z
			bestag=tag
	
	bestseq = ["S", bestag]
	
	cbt = bestag
	#Boucle qui va rechercher les étiquettes d'états précédents les plus probables, compte tenu de l'étiquette la plus probable déduite 
	#pour l'état final
	for bp in reversed(pointeurs):
		bestseq.append(bp[cbt])
		cbt=bp[cbt]
	
	bestseq.reverse()
	
	return bestseq[1:-1]
		
#Fonction testant les algorithmes d'étiquetage sur le corpus de test.
def testit(z):
	wc = 0.0	
	nice = 0.0
	errs = 0.0
	
	realcats = dict(zip(list(cats),(0 for a in list(cats))))
	
	matcon={}
	
	for ca1 in cats: 
		for ca2 in cats:
			matcon[ca1,ca2]=0
	
	for t in test:
		for w in zip(z(t),t):
			wc += 1.0
			truecat=w[1][1]
			realcats[truecat] += 1
			matcon[truecat,w[0]] += 1
			
			if w[0] == truecat:
				nice += 1.0
			else:
				errs += 1.0
	
	if MATRICE:
		#Les étiquettes de catégories réelles sont affichées à gauches
		#Les étiquettes prédites par l'algorithme sont affichées en haut
		#Il me semble que c'est conventionnel.
		
		print "Matrice de confusion :"
		z=list(cats)
		print "\t" +"\t".join(z)
		for ca in cats:
			if realcats[ca] != 0.0:
				if PERCENT:
					p=[str((100*matcon[ca,a])/realcats[ca])+"%" for a in z]
				else:
					p=[str(matcon[ca,a]) for a in z]
					
				print ca + "\t" + "\t".join(p)
	
	precision= str(100*nice/wc)+"%" if PERCENT else str(nice) + "/" + str(wc)
	print "Précision globale : " + precision  + "\n"

#Programme :
if len(args) < 1:
	print "Erreur : aucun corpus spécifié"
	sys.exit(1)

(test,matran,matrem,prevcounts,wordcounts,cats)=liredonnees(args[0])

print "Sélection de la catégorie au hasard : "
testit(randchoice) 
print "Sélection de la catégorie la plus courante : " 
testit(majoritywins(prevcounts))
print "Sélection basée sur la catégorie la plus probable de la forme" 
testit(baseline2)
print "Sélection basée sur le chemin localement optimal :"
testit(nv)
print "Sélection basée sur le chemin optimal déduit par l'algorithme de Viterbi :" 
testit(viterbi)

#Les derniers algorithmes montrent des précisions globales assez proches, 
#C'est en regardant dans les matrices de confusion qu'on voit que Viterbi est meilleur, 
#en particulier pour distinguer les clitiques et les déterminants.
#On note que les catégories sont parfois douteuse : e.g. la catégorie ET contient les mots étrangers
#Quels que soient leur contextes d'apparition. Elle mélange des mots qui appartiennent à des parties du discours différentes.
#Quand Viterbi classe 36% d'entre eux parmi les noms, j'ai plus envie de le croire lui que de croire le corpus. 

#Notons aussi que le fichier ftb2.txt fait apparaître une catégorie "Dmp" 
#Elle n'apparaît que pour le nombre trois_cent_mille, et résulte d'une erreur de formatage. 
#La ligne dit 
#trois_cent_mille	trois_cent_mille	Dmp	NA	NA	NA	NA	NA	NA
#Alors que ça devrait probablement être
#trois_cent_mille	trois_cent_mille	D	NA	m	p	NA	NA	NA


