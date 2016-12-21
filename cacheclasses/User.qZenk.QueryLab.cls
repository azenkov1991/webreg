Include qWORD

Class User.qZenk.QueryLab
{

ClassMethod InitQMSqqc244(qqc244) [ ProcedureBlock = 0 ]
{
	new quser,quserCode
	set quserCode = $G(^Q(1,244,qqc244,"quser"))
	if quserCode = "" quit -1
	set quser = ^Q(1,"Cquser",quserCode)
	if (quser'=""){
		do ##class(tdv.Util).createQmsContext(quser,,,0)
	}
	else{
		do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	}
}

/// Создает контекст QMSa от пользователя создавшего 186 объект
ClassMethod InitQMSqqc186(qqc186) [ ProcedureBlock = 0 ]
{
	new X,quser
	set X = $G(^Q(1,186,qqc186,"X"))
	set quser = $P(qW.zCnv(0,X)," ",2)
	if (quser'=""){
		do ##class(tdv.Util).createQmsContext(quser,,,0)
	}
	else{
		do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	}
}

/// Создание объекта 186 Ввод назначений для лаборатории
Query Cre186(qqc244 As %String, date As %String, time As %String, qqc174 As %String) As %Query(ROWSPEC = "qqc186:%String,status:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod Cre186Execute(ByRef qHandle As %Binary, qqc244 As %String = "", date As %String = "", time As %String = "", qqc174 As %String = "") As %Status [ Internal ]
{
	
	Set $zt="ERROR"
	If qqc244="" Quit $$$ERROR($$$InvalidParameter,"qqc244",qqc244)
	Set qHandle=1
	Set qHandle("qqc244")=qqc244
	Set qHandle("date")=date
	Set qHandle("time")=time
    Set qHandle("qqc174")=qqc174
			
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

/// d BACK^%ENT
ClassMethod Cre186Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = Cre186Execute ]
{
	Set $zt="ERROR"
	if (qHandle=1){
		set AtEnd=0,Row=..getCre186(qHandle("qqc244"),
									qHandle("date"),
									qHandle("time"),
									qHandle("qqc174"))
		set qHandle=0
	} else {set AtEnd=1,Row=""}
	Quit $$$OK

ERROR
	Set $zt="" 
	Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod Cre186Close(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = Cre186Execute ]
{
	Quit $$$OK
}

ClassMethod getCre186(qqc244 As %String, date As %String, time As %String, qqc174 As %String) [ ProcedureBlock = 0 ]
{
 do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
 // проверка параметров 
 set status = ""
 if ($D(^Q(1,244,qqc244))=0) set status = "Не существующий qqc244"
 if ($D(^Q(1,174,qqc174))=0) set status = "Не существующий qqc174"
 if status'="" set qqc186="" q $listBuild(qqc186,status)
 //если время,дата пустое или неверного формата взять занчение по умолчанию
 if (time'?2N1":"2N){
	 set time = $ZT($P($H,",",2),2)
 }
 if (date'?8N){
	 set date = $ZD($P($H,","),8)
 }
 
 s qARM( "Pars",5,244)=qqc244
 n pars,qqc235
 s qqc235=$E(qqc244,1,qW.ObjLget(235))
 s pars=qW.GG(235,"pIDo",$E(qqc244,1,qW.ObjLget(235)))_"~"_qW.GG(244,"RSpID",qqc244)_"~"_qW.GG(244,"pIDz",qqc244)_"~"_qW.GG(244,"puR",qqc244)_"~"_qW.GG(244,"pAz",qqc244)
 s qqc186=qUSER.Cre186(qqc174,date,time,,,,"Q01.01.001",pars)
 s W("u") = "Ввод_назначений (Лаборатория)"
 D qW.rCor(186,qqc186,"u",,2)
 set status = "Услуга создана"
 q $listBuild(qqc186,status)
}

/// Создание услуги в очередь
/// qqc244 - код спец-та к кому записываем.
/// qqc186 - код созданной услуги из Query.Cre186()
/// datBeg - дата начала действия очереди в формате ГГГГММДД
/// datEnd - дата окончания действия очереди в формате ГГГГММДД
/// time - время начала действия очереди (ЧЧ:ММ), окончание по умолчанию в 23:59
/// Du - код ОКМУ назначаемой услуги
/// labParam - параметры через ~ лабораторного назначения(необязательные)
/// 	lo лабораторный образец
/// 	pCodKO код контингента обследованных
/// 	pPregWeek срок беременности в неделях
/// 	qlsClinCode	клинические условия
/// 	Mheight	рост пациета 
/// 	Mweight	вес пациента
/// 	MdayDiur суточный диурез
/// 	MqlsCmnt примечание для лаборатории
/// 	
/// если назначение создано возвращает qqc1860 и статус (проверка существования назначенной услуги)
Query Cre1860(qqc244 As %String, qqc186 As %String, datBeg As %String, datEnd As %String, time As %String, Du As %String, labParam) As %Query(ROWSPEC = "qqc1860:%String,tmpNumber:%String,status:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod Cre1860Execute(ByRef qHandle As %Binary, qqc244 As %String = "", qqc186 As %String = "", datBeg As %String = "", datEnd As %String = "", time As %String = "", Du As %String = "", labParam = "") As %Status [ Internal ]
{
	// look at %Library.Global for direct ^CacheTemp/^CacheTempNodes use with multi-row return possibility

	Set $zt="ERROR"
	If qqc244="" Quit $$$ERROR($$$InvalidParameter,"qqc244",qqc244)
	Set qHandle=1
	Set qHandle("qqc244")=qqc244
	Set qHandle("qqc186")=qqc186
	Set qHandle("datBeg")=datBeg
    Set qHandle("datEnd")=datEnd
	Set qHandle("time")=time
	Set qHandle("Du")=Du
	Set qHandle("labParam")=labParam
	  
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod Cre1860Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = Cre1860Execute ]
{
	Set $zt="ERROR"
	
	if (qHandle=1){
		set AtEnd=0,Row=..getCre1860(qHandle("qqc244"),
									qHandle("qqc186"),
									qHandle("datBeg"),
									qHandle("datEnd"),
									qHandle("time"),
									qHandle("Du"),
									qHandle("labParam"))
		set qHandle=0
	} else {set AtEnd=1,Row=""}
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod Cre1860Close(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = Cre1860Execute ]
{
	Quit $$$OK
}

ClassMethod getCre1860(qqc244 As %String, qqc186 As %String, datBeg As %String, datEnd As %String, time As %String, Du As %String, labParam As %Library.String = "") [ ProcedureBlock = 0 ]
{
 do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
 set $zt="ERROR"
 // проверка входных параметров
 set status = ""
 if ($D(^Q(1,244,qqc244))=0) set status = "Не существующий qqc244"
 if ($D(^Q(1,186,qqc186))=0) set status = "Не существующий qqc186"
 if (((datBeg'="")&&(datEnd'=""))&&($ZDH(datEnd,8)<$ZDH(datBeg,8))) {set status = "Некорректный интервал времени"}
 if status'="" quit $listBuild(qqc1860,status)
 
 //если время,дата пустое или неверного формата взять значение по умолчанию
 if (time'?2N1":"2N){
	 set time = $ZT($P($H,",",2),2)
 }
 if (datBeg'?8N){
	 set datBeg = $ZD($P($H,","),8)
 }
 if (datEnd'?8N){
 	set datEnd = $ZD(($ZDH(datBeg,8) + 7),8)
 }
 
 n qqc1860,pars,status,currentDu,qqc235
 s pIDo = qW.GG(235,"pIDo",$E(qqc244,1,qW.ObjLget(235)))
 s pID = qW.GG(244,"RSpID",qqc244)
 s pIDz = qW.GG(244,"pIDz",qqc244)
 s pars=pIDo_"~"_pID_"~"_pIDz_"~"_qW.GG(244,"puR",qqc244)_"~"_qW.GG(244,"pAz",qqc244)
 s qqc1860=""
 s qqc235=$E(qqc244,1,qW.ObjLget(235))
 
 s pars=qW.GG(235,"pIDo",qqc235)_"~"_qW.GG(244,"RSpID",qqc244)_"~"_qW.GG(244,"pIDz",qqc244)_"~"_qW.GG(244,"puR",qqc244)_"~"_qW.GG(244,"pAz",qqc244)_"~"_qW.GG(235,"sK",qqc244)_"~"_qW.GG(244,"sS",qqc244)_"~"_qW.GG(244,"sZ",qqc244)_"~"_qW.GG(244,"sP",qqc244)_"~"_qW.GG(244,"n634",qqc244)_"~"_qW.GG(244,"n647",qqc244)
 s currentDu=qW.GtoExt("8N",qW.GG(1860,"Dn",qW.FastKey(1860,"Du",,1,Du,$E(qqc186,1,qW.ObjLget(174)))))
 s:currentDu'="" currentDu=$S(((datBeg>=$E(currentDu,13,20))&&(datBeg<=$E(currentDu,1,8)))||((datEnd>=$E(currentDu,13,20))&&(datEnd<=$E(currentDu,1,8))):1,1:"")
 s currentDate=$P($ZDT($H,8)," ")_","_$P($ZDT($H,8)," ",2)_","_$P($ZH,".",2)
 /// проверка уже назначенной первой услуги в очередь 
 i (currentDu="")&&(qW.GG(186,"u",qqc186)'="") {
 	s W("attExternal")=1
	s qqc1860=..create1860lab(qqc186,datBeg,datEnd,time,qqc244,Du,,pars,1,,labParam)
 	s status="назначение создано"
 }
 else {
 s status="назначение не создано, "_$S(qW.GG(186,"u",qqc186)="":qqc186_" некорректный",1:"уже существует "_Du)
 ;s ^QMSlog("Query.Cre1860",currentDate)="status="_status_" | qqc1860="_qW.FastKey(1860,"Du",,1,Du,$E(qqc186,1,qW.ObjLget(174)))_"("_qW.GtoExt("8N",qW.GG(1860,"Dn",qW.FastKey(1860,"Du",,1,Du,$E(qqc186,1,qW.ObjLget(174)))))_";"_datBeg_";"_datEnd_")"
 }

 quit $listBuild(qqc1860,qW.GG(1860,"nlab",qqc1860),status)
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod create1860lab(qqc186 As %Library.String, datAF As %Library.String, dE As %Library.String, pPN As %Library.String, qqc244 As %Library.String, Du As %Library.String, pcon As %Library.String, pars As %Library.String, Mn As %Library.String, Mtpl As %Library.String, labParam As %Library.String = "") [ ProcedureBlock = 0 ]
{
 new qqc174,qqc196,qqw,qqc235u,qqc235,qqc83,index,par,paramNameList,paramCount,clinCode,clinCodes,qqcLo,lo,loi
 
 ; добываем эпизод
 S qqc174=$E(qqc186,1,10)
 
 ; время назначения
 S:$G(pPN)="" pPN="00:00"
 

 ; код услуги, приоритет, плательщик
 F qqw="Du","pcon","Mtpl" S W(qqw)=$G(@qqw)
 
 
 
 set pars = $TR(pars," ","_")
 
 ; параметры специалиста
 F qqw=1:1:11 S W($P("pIDo pID pIDz puR pAz sK sS sZ sP n634 n647"," ",qqw))=$P(pars,"~",qqw)
 
 ; организация
 S qqc235=qW.FastKey(235,"pIDo","",1,W("pIDo"),"",,,"NR")
 
 ; организация для услуги
 S qqc235u=qUSER.qqc235u(qqc235)
 
 set addConceptList = ""
 
 ; услуга
 S W("lo")="",W("tn")="" 
 D:W("Du")'=""
 .S qqc83=$$$FKey(83,"Du","",1,W("Du"),qqc235u) I qqc83="" S:qqc235u'="#AB" qqc83=$$$FKey(83,"Du","",1,W("Du"),"#AB") I qqc83="" S W("u")="???",W("lo")="",W("tn")="" Q
 .S W("u")=qW.GG(83,"u",qqc83)
 .S W("tn")=qW.GG(83,"tn",qqc83)
 .S lo = qW.GG(83,"lo",qqc83)
 .I lo[" " D
 ..F index = 1:1 S loi = $P(lo," ",index)  Q:loi=""  D
 ...I loi'["|Y" S $P(lo," ",index)=""
 .S lo=$Replace(lo,"|Y","") S lo = $ZSTRIP(lo,"<=>"," ")
 .S W("lo") = lo
 .S:W("lo")="" W("lo") = $P(qW.GG(83,"lo",qqc83)," ",1)
 .S qqwchg83="Du Dui u tn tu qlsLk"
 .S W("X5240") = 7
 .D qW.GWlist(83,qqwchg83 ,qqc83)
 
 
 D  
 .; очередь
 .S (W("Mnr"),W("Mn"))=1,W("datAF")=0,(W("dE"),W("pPN"))=""
 .
 .; интервал действия
 .S max=qUSER.oDef235(qqc235, "Mdod")
 .I $G(dE)="" D
 ..I max'>0 S dE=datAF Q
 ..S dE=$ZD($ZDH(datAF,8)+max,8)
 .
 .S W("Dn")=qW.GtoExt("I",dE_"2359"_"<<"_datAF_$TR(pPN,":"))
 
 ;номер назначения
 S W("n")=qW.rIncM("Mn",1,174,qqc174)
 
 /// Создание дополнительного персонала
 i ((qUSER.oDef244(qqc244,"MpID2v")=1)||(qUSER.oDef244(qqc244,"@MpID.2")'=""))&&(qW.GG(83,"Md",qW.FastKey(83,"Du",,1,Du,qqc235))=1) {
 s W("Md")=1 ;s W("R2pIDo")=W("pIDo"),W("R2pID")=W("pID"),W("R2pIDz")=W("pIDz")
 }
 set qqc1860 = $P(qW.rNew(1860,qqc186)," ")
 
 D qW.rCor(1860,qqc1860,"Md Mnr R2pIDo R2pID R2pIDz attExternal n Mn Dn datAF dE pPN Ytr pIDo pID pIDz puR pAz sK sS sZ sP n634 n647 Du Dui u tn tu qlsLk lo X5240 pcon Mtpl"_$S(addConceptList'="":" "_addConceptList,1:""),,,,,,1) ;Без триггега qUSER.Cor1860
 s ^Q(1,1860,qqc1860,"Xc")=qW.zCnv(1,$P($H,",")_","_$P($H,",",2),"web")

 D
 .D
 ..S pPN=qUSER.CreQNazM($TR($P(pars,"~",1,3),"~"," "),0,,qqc1860)
 ..S W("pPN")=pPN
 ..D qW.rCor(1860,qqc1860,"pPN",,0,,,,1)
 .
 .; также в admRdRadd1860
 .S W("Mn")=Mn
 .D qW.rCor(1860,qqc1860,"Mn",,0,,,,1)
 do SetTmpNumber() 
 d qW.rCor(1860,qqc1860,"nlab",,0,,,,1)
 
 // ИФ
 //Поиск 196 ОМС
 set qqc196 = qW.UserOrd(1,196,,qqc174,,"qW.G(""DGID.1600"")'=""""")
 if (qqc196'=""){
 	set Oplata("tpl")="ОМС"
 	set Oplata("Mtpl")=1
 	set Oplata("DGID.196")=qW.GG(196,"DGID",qqc196)
 	D qFSrc.setTo1860ByParam(qqc1860,"Oplata")
 }
 
 
 // Установка дополнительных параметров лабораторного назначения
 if labParam'="" {
 set paramNameList = "lo~pCodKO~pPregWeek~qlsClinCode~Mheight~Mweight~MdayDiur~MqlsCmnt"
 set paramCount = 8
 
 // Проверка дополнительных параметров на валидность
 // lo - должен быть указан в настройке услуги
 set lo = $P(labParam,"~",1)
 for index=1:1{
 	set loi = $P(lo," ",index) 
 	q:loi=""
 	if (qW.GG(83,"lo",qqc83)'[loi){
 		set $P(lo," ",index) = ""
 	}
 }
 set lo = $ZSTRIP(lo,"<>"," ")
 set $P(labParam,"~",1) = lo
 
 // pCodKO - должен быть в справчнике
 if (qW.FastKey("KO","pCodKO","",1,$P(labParam,"~",2),qqc235)=""){
 	set $P(labParam,"~",2) = ""
 }
 // pPregWeek - число меньше 43
 if (($P(labParam,"~",3)'?1.2N)||($P(labParam,"~",3)>42)){
 	set $P(labParam,"~",3) = "" 
 }
 // qlsClinCode - должен быть в справочнике несколько значений через пробел
 set clinCodes = $P(labParam,"~",4)
 for index = 1:1{
	set clinCode = $P(clinCodes," ",index)
	q:clinCode=""
 	if (qW.FastKey("qlsClin","qlsClinCode","",1,clinCode,qqc235)=""){
		set $P(clinCodes," ",index) = ""
 	}
 }
 set clinCodes = $ZSTRIP(clinCodes,"<=>"," ")
 set $P(labParam,"~",4) = clinCodes
 
 // MHeight - число меньше 240
 if (($P(labParam,"~",5)'?1.3N)||($P(labParam,"~",5)>240)){
 	set $P(labParam,"~",5) = "" 
 }
 // Mweight - число меньше 300
 set $P(labParam,"~",6) = +$P(labParam,"~",6)
 if (($P(labParam,"~",6)>300)||($P(labParam,"~",6)<=0)){
 	set $P(labParam,"~",6) = "" 
 }
 // MdayDiur - число максимум 4 знака
 set $P(labParam,"~",7) = +$P(labParam,"~",7)
 if ($l($P(labParam,"~",7))>4){
 	set $P(labParam,"~",7) = "" 
 } 
 set qqwchg=""	
 
 for index = 1:1:paramCount{
 	 set parValue = $P(labParam,"~",index)
 	 if parValue="" continue
 	 set parName = $P(paramNameList,"~",index)
 	 set W(parName) = parValue
 	 set qqwchg = qqwchg_parName_" "
 }
 do qW.rCor(1860,qqc1860,qqwchg,,,,,,1)
 
 	
 }
 
 quit qqc1860
 // установка в  W("nlab") лабораторного номера
SetTmpNumber()
 new qqcP, datb,MIndTal,MindTalDu,qlsVR,nlab0,newnlab,q1860,TMPrule,TMPruleN 
 //добавление TMP номера
 S qqcP=qqc1860
 S datb = datAF
 s MIndTal =+qUSER.oDef235(1,"MIndTal",,0) 
 s MIndTalDu = qW.GG(1860,"@Du83.MIndTal",qqcP) 
 s qlsVR = qW.GG(83,"qlsVR",qqc83)
 kill W("nlab")
 ; правило формирования лаб.номеров "qlsTMPrule" (объединение услуг в течении дня): 
 ; 1) Место_забора
 ; 2) Место_забора_/_Образец
 ; 3) Место_забора_/_Образец_/_Контейнер
 s TMPrule=$TR(qUSER.oDef235(1,"qlsTMPrule",,"ВРЕМЕННЫЙ_TMP-НОМЕР")," ","_") s:TMPrule="" TMPrule="Место_забора"
 s TMPruleN=$l(TMPrule,"/") ;вычисляем код для правила
 
 
 s newnlab = qW.GG(83,"qlsLNnew",qqc83)
 i +$G(newnlab)=0 D  
 . s (qqc1860,q1860,nlab0)="" 
 . f  s qqc1860=qW.FastKey(1860,"tn pIDo pID pIDz"_$S(TMPruleN>1:" lo",1:"")_$S(TMPruleN>2:" qlsLk",1:""),qqc1860,,"Лаборатория"_"~"_pIDo_"~"_pID_"~"_pIDz_$S(TMPruleN>1:"~"_$P(lo," "),1:"")_$S(TMPruleN>2:"~"_$P(qlsLk," "),1:""),qqc174) q:qqc1860=""  d  q:q1860'=""
 .. i $l(qW.GG(1860,"n",qqc1860),".")>1 quit   ;отсекаем забранные/переданные/авторизованные + выполненные услуги
 .. s datAF=qW.GG(1860,"datAF",qqc1860)
 .. i datAF=0 s dn=$E(qW.GtoExt("8N",qW.GG(1860,"Dn",qqc1860)),13,20)  ;дата начала действия очереди
 .. i datAF'=0 s dn=datAF_qW.GG(1860,"pPN",qqc1860)
 .. i ((qW.GG(1860,"nlab",qqc1860)'="")&&(datb=dn)) s q1860=qqc1860 ; s ^mtempLIS($i(^mtempLIS),qqcP,"qqc1860")="ok "_q1860
 .. quit:q1860=""
 .. ; ---
 .. ; проверяем, был ли установлен флаг "Новый лаб.номер" для найденной услуги
 .. ; если мы нашли услугу из комплекса, то доп.проверяем флаги на 2-х уровнях (комплекс и услуга)
 .. i $E(qqc1860,1,21)'=$E(qqcP,1,21)&&($P(qLS.dataUsl(qARM("Pars",3),qW.GG(1860,"Du",$E(qqc1860,1,21))),$C(1),7)=1) s q1860="" quit
 .. i $l(qqc1860)>21,$P(qLS.dataUsl(qARM("Pars",3),qW.GG(1860,"Du",qqc1860)),$C(1),7)=1 s q1860="" quit
 .. ; ---
 .. ; проверяем, "подходящее" ли назначение мы нашли  
 .. ; если установлен счетчик "СИСТЕМНЫЙ", то для каждого назначения формируется свой уникальный номер
 .. i $G(q1860)'="" d
 ... i (qW.GG(1860,"nlab",q1860)'["TMP")&&(qlsVR'=1) s q1860="" q   ;если нашли не ТМР-номер, а услуга не экспресс, то номер не походит
 ... i (qW.GG(1860,"nlab",q1860)["TMP")&&(qlsVR=1) s q1860="" q    ;если нашли ТМР-номер, а услуга экспресс, то номер не походит
 ... ; для "Экспресса" доп.проверка - если хоть одна услуга уже была выполнена из этого лаб.номера, то этот номер не берем
 ... i qlsVR=1 do  q:q1860=""
 .... ;i qW.FastKey(186,"nlab pANdop","",0,qW.GG(1860,"nlab",q1860)_"~выполнено",$E(q1860,1,$$$ObjLget(174))) s q1860=""
 .... i qW.FastKey(186,"nlab","",0,qW.GG(1860,"nlab",q1860),$E(q1860,1,$$$ObjLget(174))) s q1860=""   ;18/03/2011 @gol
 ... ; проверяем "Индекс для печати"  @gol 16/08/2011
 ... i +$G(MIndTal)=1&&(qW.GG(1860,"@Du83.MIndTal",q1860)'=MIndTalDu) s q1860="" q
 ... ; Если нашли "подходящее" назначение, то берем лаб.номер с этой услуги
 ... s nlab0=qW.GG(1860,"nlab",q1860)
 . ; ---
 s:$G(nlab0)'="" W("nlab")=nlab0
 ; Если не нашли "подходящее" назначение, то формируем новый лаб.номер
 i $G(W("nlab"))="" s W("nlab") = qUSER.GetCount(235,"Ynlab",qqc235,$S(qlsVR=1:"ЕЖЕДНЕВНЫЙ",1:"ВРЕМЕННЫЙ_TMP-НОМЕР"),1860,"nlab")
 S qqc1860=qqcP
 q
}

}

