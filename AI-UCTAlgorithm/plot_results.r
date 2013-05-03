ggplot(df, aes(x=pomiar,y=wynik,group=group))+geom_line(linetype="solid",size=1.5)+geom_point(aes(colour=group),shape=18,size=10)
df = data.frame(wynik = wynik, group = as.factor(rep(c(0,1,1,0),14)), pomiar = as.integer( ((1:28) -1)/2



ggplot(df, aes(x=pomiar,y=wynik,group=group))+ xlab("Rozgrywka")+ylab("Wynik gry")+geom_bar(data=df[df[,"group"]==0,],stat="identity",aes(fill=group,group=group))+geom_bar(data=df[df[,"group"]==1,],stat="identity",aes(fill=group, group=group))+ggtitle("UCTAgent [0] vs Greedy [1]")

wyniki = c(119, 507, 279, 347, 161, 465, 348, 278, 118, 508, 314, 312, 137, 489, 319, 307, 169, 457, 354, 272, 176, 450, 349, 277, 243, 383, 403, 223)

df = data.frame(wynik = wyniki, Gracz = rep(c(0,1,1,0),7), pomiar = as.integer((1:28-1)/2))

ggplot(df, aes(x=pomiar,y=wynik,group=Gracz))+ xlab("Rozgrywka")+ylab("Wynik gry")+geom_bar(data=df[df[,"group"]==0,],stat="identity",aes(fill=Gracz,group=Gracz,alpha=0.6))+geom_bar(data=df[df[,"group"]==1,],stat="identity",aes(fill=group, group=group,alpha=0.6))+ggtitle("UCTAgent+ transpozycje + e-greedy [0] vs UCTAgent + transpozycje [1]")






wyniki=
c(300, 289, 254, 335, 334, 255, 221, 368, 274, 315, 185, 404, 289, 300, 247, 342, 314, 275, 276, 313, 247, 342, 272, 317, 143, 446, 187, 402)


