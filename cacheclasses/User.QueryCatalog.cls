Include qWORD

Class User.QueryCatalog Extends (%RegisteredObject, %SOAP.WebService) [ Inheritance = right ]
{

Parameter SERVICENAME = "QueryCatalog";

// ======================================================================

/// callback - основной метод выборки из базы заносит в ^||result все необходимое
/// Функция callback должна положить в ^||result строки запроса
/// qHandle(1) - первый параметр qHandle qHandle(2) - второй параметр...
ClassMethod GeneralExecute(ByRef qHandle As %Binary, callback, args...) As %Status [ ProcedureBlock = 0 ]
{
	set $zt="ERROR"
	set qHandle=""
	set ^||result =0
	// передача параметров через qHandle

	for count = 1:1:args{
    	set qHandle(count) = $G(args(count))
    }
	// параметры функции в qHandle
    do $classmethod($This,callback,.qHandle)

	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod GeneralClose(ByRef qHandle As %Binary) As %Status
{
	kill ^||result
	Quit $$$OK
}

ClassMethod GeneralFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status
{
	Set $zt="ERROR"
	Set idx=qHandle
	
	Set idx=$Order(^||result(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=^||result(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod InitQms() [ ProcedureBlock = 0 ]
{
	do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	q
	set qARM("Password")="XXXX drowq"
 	set qARM("Pars",9)="S qqend=1"
    set qARM=##class(%TqARM).%New() do qARM.Create()
	set qWEB=##class(%qWEB).%New()
 	set qSYS=##class(%qSYS).%New()
	set qW=##class(%qWORD).%New()
  	set qview="XXXX"
 	set qqnump=0 set Vo(qqnump)=qview
 	set Vo(qqnump,-1,21)=0
 	set qqred=""
}

/// Создает контекст QMSa от пользователя создавшего 186 объект
ClassMethod InitQMSqqc186(qqc186) [ ProcedureBlock = 0 ]
{
	new quser
	set qARM=##class(Library.TqARM).%New() do qARM.Create()
	set quser = qW.GG(244,"quser",qUSER.qqc244(qW.GG(186,"pIDo",qqc186),qW.GG(186,"pID",qqc186),qW.GG(186,"pIDz",qqc186)))
	if (quser'=""){
		do ##class(tdv.Util).createQmsContext(quser,,,0)
	}
	else{
		do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	}
}

/// Для тестирования функционала записи в расписание
ClassMethod SetFakeRaspOnSunday(qqc244, time, date = "") As %String [ ProcedureBlock = 0 ]
{
   	if ($G(date)="" || $$getDayWeek'=6){
		set currentDayWeek = $$getDayWeek($ZD($H,8))
		set dayToSunday = 6 - currentDayWeek
		set firstSunday = $H + dayToSunday
		set date = $ZD(firstSunday, 8)
   	}
   	if $D(^Q(1, 244, qqc244)){
   		set ^Q(1, 244, qqc244, "Ytr", date)=date_"~7~~~~~~~~~~~~~~~~~~"
		set index=""
		set index = $O(^Q(1, 244, qqc244, "Ytr",date,index),-1) + 1
		set ^Q(1, 244, qqc244, "Ytr",date,index)=time_"~7~~~~~~~~~~СТОМАТОЛОГИЯ~~~~~~~~"_$ZD($H,3)_" 16:46 ЗенковАЛ"
   	}
	quit date
getDayWeek(date)
	quit ($ZDH(date,8)#7 + 3)#7
}

ClassMethod DeleteFakeRasp(qqc244, date) As %Boolean [ ProcedureBlock = 0 ]
{
	if $$getDayWeek(date)=6{
		if $D(^Q(1, 244, qqc244)){
			k ^Q(1, 244, qqc244, "Ytr", date)
		}
	}
	quit 1
}

/// Возврашает краткую специалзацию врача
ClassMethod GetSpec(qqc244) [ ProcedureBlock = 0 ]
{
	new spec, n634, nResqqc, lspec, n637
	set spec = qW.GG(244,"@puR.k",qqc244)
	// Если краткой специализации нет в справочники nRes2 
	// то поиск наличия кратких названий в специализации
	set n634 = qW.GG(244,"n634",qqc244)
	set nResqqc = qW.FastKey("nRes2","n634","",1,n634,$E(qqc244,1,3))
	set lspec = qW.GG("nRes2","n637",nResqqc)
	if (lspec = ""){
		set n637 = ""
		for {
			set n637 = $O(^Q(1,"n637",n637))
			quit:n637=""
			if spec[$E(n637,2,*) set spec = n637 quit
		}
	}
	if (qW.GG(244,"@puR.t",qqc244)="Кабинет") set spec = "Кабинет"
	quit spec
}

// ======================================================================

// =======================================================================

/// Справочник контингент обследованных
Query Contingent(pIDo As %String) As %Query(ROWSPEC = "Code:%String,Contingent:%String,Activity:%Boolean") [ SqlProc, WebMethod ]
{
}

ClassMethod ContingentExecute(ByRef qHandle As %Binary, pIDo As %String) As %Status
{
	Set $zt="ERROR"
	Set qHandle=""
	Set ^||result =0
    do ..getContingent(pIDo)

	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod ContingentClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = ContingentExecute ]
{
	kill ^||result
	Quit $$$OK
}

ClassMethod ContingentFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = ContingentExecute ]
{
	Set $zt="ERROR"
	Set idx=qHandle
	Set idx=$Order(^||result(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=^||result(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod getContingent(pIDo) [ ProcedureBlock = 0 ]
{
 	do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"qW.G(""pIDo"")="""_pIDo_"""")
	
	set qqcKO = ""
	for
	{
		set qqcKO = qW.UserOrd(1,"KO",qqcKO,qqc235)
		q:qqcKO=""
		set Code = qW.GG("KO","pCodKO",qqcKO)
		set Contingent = qW.GG("KO","pKO",qqcKO)
		set Activity = qW.GG("KO","qlsAct",qqcKO)
		set ^||result(qqcKO) = $LISTBUILD(Code,Contingent,Activity) 
		
	}
	q
}

/// Справочник клинических условий для лаборатории
Query ClinicalLabCondition(pIDo As %String) As %Query(ROWSPEC = "Code:%String,Name:%String,Gender:%String,PatientAge:%String,Activity:%Boolean") [ SqlProc, WebMethod ]
{
}

ClassMethod ClinicalLabConditionExecute(ByRef qHandle As %Binary, pIDo As %String) As %Status
{
	Set $zt="ERROR"
	Set qHandle=""
	Set ^||result =0
    do ..getClinicalLabCondition(pIDo)

	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod ClinicalLabConditionClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = ClinicalLabConditionExecute ]
{
	kill ^||result
	Quit $$$OK
}

ClassMethod ClinicalLabConditionFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = ClinicalLabConditionExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getClinicalLabCondition(pIDo) [ ProcedureBlock = 0 ]
{
	do ..InitQms()
	new qqc, Code, Name, Gender, PatientAge, Activity,qqc235
	set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"qW.G(""pIDo"")="""_pIDo_"""")
	set qqc = ""
	for
	{
		set qqc  = qW.UserOrd(1,"qlsClin",qqc,qqc235)
		q:qqc=""
		set Code = qW.GG("qlsClin","qlsClinCode",qqc)
		set Name = qW.GG("qlsClin","qlsClinName",qqc)
		set Gender = qW.GG("qlsClin","qlsPol",qqc)
		set PatientAge = qW.GG("qlsClin","qlsAge",qqc)
		set Activity = qW.GG("qlsClin","qlsAct",qqc)
		set ^||result(qqc) = $LISTBUILD(Code,Name,Gender,PatientAge,Activity)
	
	}
	q
}

/// Словарь Тип сессии
Query DepConst(SessionType As %String) As %Query(ROWSPEC = "DepartmentCode:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod DepConstExecute(ByRef qHandle As %Binary, SessionType As %String) As %Status
{
	Set $zt="ERROR"
	Set qHandle=""
	Set ^||result =0
    do ..getDepConst(SessionType)
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod DepConstClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = ContingentExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod DepConstFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = ContingentExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getDepConst(tses) [ ProcedureBlock = 0 ]
{
		
	do ..InitQms()
	new qqc, qqcWW,pidList, index, pID
	set qqc = ""
	set qqcWW = qW.FastKey("ww","tses","",1,tses,"vAB")
	if qqcWW="" quit
	set pidList = qW.GG("ww","RepID",qqcWW)
	for index =1:1:$length(pidList," "){
		set pID = $P(pidList," ",index)
		q:pID=""
		set ^||result(index) = $LB(pID)
	}
	
	q
}

// =======================Дочерние подразделения========================

Query ChildDepartments(qqc As %String) As %Query(ROWSPEC = "qqc:%String,Name:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod ChildDepartmentsExecute(ByRef qHandle As %Binary, qqc As %String) As %Status
{
	Set $zt="ERROR"
	Set qHandle=""
	Set ^||result =0
    do ..getChildDepartments(qqc)
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod ChildDepartmentsClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = ContingentExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod ChildDepartmentsFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = ContingentExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getChildDepartments(qqc153) [ ProcedureBlock = 0 ]
{
	do ..InitQms()
	new pID
 	set pID = qW.GG(153,"pID",qqc153)
 	
 	//для объекта выбрать все дочерние
	set qqc153 ="" 
	for{
		set qqc153 = $Order(^Q(1,"pID",pID,153,qqc153)) 
		q:qqc153=""
		if ($Data(^Q(1,"pID",pID,153,qqc153,"S"))'=0){ 
			set ^||result(qqc153) = $LB(qqc153,qW.GG(153,"fio",qqc153))
		}
	}
}

// =======================Список сотрудников========================

Query ResoursesForDepartment(qqc153 As %String) As %Query(ROWSPEC = "qqc:%String,Name:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod ResoursesForDepartmentExecute(ByRef qHandle As %Binary, qqc As %String) As %Status
{
	Set $zt="ERROR"
	Set qHandle=""
	Set ^||result =0
    do ..getResoursesForDepartment(qqc)
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod ResoursesForDepartmentClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = ResoursesForDepartmentExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod ResoursesForDepartmentFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = ResoursesForDepartmentExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getResoursesForDepartment(qqc153) [ ProcedureBlock = 0 ]
{
	do ..InitQms()	
	new pID, qqc244
 	set pID = qW.GG(153,"pID",qqc153)
 	
 	//для объекта выбрать все дочерние
	set qqc244 ="" 
	for{
		set qqc244 = $Order(^Q(1,"pID",pID,244,qqc244)) 
		q:qqc244=""
		if ($Data(^Q(1,"pID",pID,244,qqc244,"S"))'=0){ 
			set ^||result(qqc244) = $LB(qqc244,$Replace(qW.GG(244,"pAz",qqc244),"_"," "))
		}
	}
}

/// Возращает qqc174 открытого эпизода содержащего услугу со специализацией 
/// совпадающей со специализацией переданного qqc244
/// Дата выполнения услуги  
Query GetPreviousqqc174(qqc153 As %String, qqc244 As %String, numOfDays As %String, date As %String) As %Query(ROWSPEC = "qqc174:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod GetPreviousqqc174Execute(ByRef qHandle As %Binary, qqc153 = "", qqc244 = "", numOfDays = "", date = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"getPreviousqqc174",qqc153,qqc244,numOfDays,date)
}

ClassMethod GetPreviousqqc174Close(ByRef qHandle As %Binary) As %Status [ PlaceAfter = GetPreviousqqc174Execute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod GetPreviousqqc174Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = GetPreviousqqc174Execute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

/// Непосредственно сам поиск
ClassMethod getPreviousqqc174(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	set $zt = "testerror"
	new date,qqc153,qqc244,numOfDays
	do ..InitQms()
	set qqc153 = qHandle(1)
	set qqc244 = qHandle(2)
	set numOfDays = qHandle(3)
	set date = qHandle(4)
	if date="" set date= $ZD($H,8)
	if numOfDays="" set numOfDays=30
	set n647 = qW.GG(244,"n647",qqc244)
	set ^||result(1) =""
	
	for dateIH = ($ZDH(date,8)-numOfDays):1:$ZDH(date,8){
		set dateI = $ZD(dateIH,8)
		set tn="Консультация Посещение"
		for i=1:1:$L(tn){
			S tni=$P(tn," ",i),qqct=""
			for {
				S qqct=qW.FastKey(1860,"tn datAF",qqct,1,tni_"~"_dateI,qqc153,,,"(qOrdUsl.getn647()="""_n647_""")")
		   		Q:qqct="" 
		    	// Все найденные услуги занести в массив qqc1860list
				set qqc1860list(dateI,qqct) = ""
			}
		}
	}
	// Цикл по найденным услугам
	set quitFlag=0 
	set dateI =""
	for{
		set dateI=$Order(qqc1860list(dateI),-1)
		quit:dateI=""
		quit:quitFlag
		set qqc1860 =""
		for{
			set qqc1860=$Order(qqc1860list(dateI,qqc1860),-1)
			quit:qqc1860=""
			set qqc174 = $E(qqc1860,1,qW.ObjLget(174))
			if ((qW.GG(174,"pvs",qqc174)="АМБУЛАТОРНО")&&(qW.GG(174,"pAG",qqc174)="")){
				set ^||result(1) = $LB(qqc174)  set quitFlag=1 quit
			}
		}
	}
 	q
testerror
	set ^||result(1) = $LB($ze)
	q
}

/// Запись номера телефона
/// PhoneType
/// 1 = домашний телефон
/// 2 = мобильный телефон
/// 3 = рабочий телефон
/// internationalFlag - 1,0 флаг международный номер
Query UpdatePatientPhoneNumber(qqc153 As %String, phoneNumber As %String, internationalFlag As %Boolean, phoneType As %Integer) As %Query(ROWSPEC = "Status:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod UpdatePatientPhoneNumberExecute(ByRef qHandle As %Binary, qqc153 = "", phoneNumber = "", internationalFlag = "", phoneType = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"setPhoneNumber",qqc153,phoneNumber,internationalFlag,phoneType)
}

ClassMethod UpdatePatientPhoneNumberClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = UpdatePatientPhoneNumberExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod UpdatePatientPhoneNumberFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = UpdatePatientPhoneNumberExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

/// Непосредственно сам поиск
ClassMethod setPhoneNumber(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new qqc159
	do ##class("tdv.Util").createQmsContext("ЗенковАЛ",,,0)
	
	set qqc153 = qHandle(1)
	set phoneNumber = qHandle(2)
	set internationalFlag = qHandle(3)
	set phoneType = qHandle(4)
	
	set:phoneType="" phoneType = 2
	if (qqc153=""||'$D(^Q(1,153,qqc153))) set ^||result(1) = $LB("Error: patient don't exist") q
	
	set phoneType = $Case(phoneType,1:"домашний",2:"мобильный",3:"рабочий",:"мобильный")
	
	// Если есть удалить
	set qqc159 = qW.FastKey(159,"pTtype",,1,phoneType,qqc153)

	if qqc159=""{
		set qqc159 = $P(qW.rNew(159,qqc153)," ",1)
		set:internationalFlag="" internationalFlag=0
		set W("pTw") = +internationalFlag
		set W("pT") = phoneNumber
		set W("pTtype") = phoneType
		do qW.rCor(159,qqc159,"pT pTtype pTw") 
	}
	else{
		set W("pT") = phoneNumber
		if (internationalFlag'=""){
			set W("pTw") = +internationalFlag
			do qW.rCor(159,qqc159,"pT pTw")
		}else{
			do qW.rCor(159,qqc159,"pT")
		}
	
	}
	
	set ^||result(1) =$LB("") quit
}

Query patientPhoneNumbers(qqc153 As %String) As %Query(ROWSPEC = "Type:%String,Phone:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod patientPhoneNumbersExecute(ByRef qHandle As %Binary, qqc153 = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"getPhoneNumbers",qqc153)
}

ClassMethod patientPhoneNumbersClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = UpdatePatientPhoneNumberExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod patientPhoneNumbersFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = UpdatePatientPhoneNumberExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

/// Непосредственно сам поиск
ClassMethod getPhoneNumbers(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new qqc159,qqc153,counter
	k ^||result
	do ##class("tdv.Util").createQmsContext("ЗенковАЛ",,,0)
	
	set qqc153 = qHandle(1)
	set qqc159=""
	set counter=0
	for{
		set qqc159=qW.UserOrd(1,159,qqc159,qqc153,,"qW.zTmpI(1)")
		q:qqc159=""
		set ^||result(counter)=$LB(qW.GG(159,"pTtype",qqc159),qW.GG(159,"pT",qqc159))
		set counter = counter + 1
	}
}

/// Запись номера телефона на 153
Query UpdatePatientPhoneNumber153(qqc153 As %String, phoneNumber As %String) As %Query(ROWSPEC = "Status:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod UpdatePatientPhoneNumber153Execute(ByRef qHandle As %Binary, qqc153 = "", phoneNumber = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"setPhoneNumber153",qqc153,phoneNumber)
}

ClassMethod UpdatePatientPhoneNumber153Close(ByRef qHandle As %Binary) As %Status [ PlaceAfter = UpdatePatientPhoneNumber153Execute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod UpdatePatientPhoneNumber153Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = UpdatePatientPhoneNumber153Execute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod setPhoneNumber153(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new qqc153
	do ##class("tdv.Util").createQmsContext("ЗенковАЛ",,,0)
	
	set qqc153 = qHandle(1)
	set phoneNumber = qHandle(2)

	if (qqc153=""||'$D(^Q(1,153,qqc153))) set ^||result(1) = $LB("Error: patient don't exist") q
	set W("pT") = phoneNumber
	do qW.rCor(153,qqc153,"pT") 
	set ^||result(1) =$LB("") quit
}

Query delete186(qqc186 As %String) As %Query(ROWSPEC = "ok:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod delete186Execute(ByRef qHandle As %Binary, qqc186 = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"delete186func",qqc186)
}

ClassMethod delete186Close(ByRef qHandle As %Binary) As %Status [ PlaceAfter = delete186Execute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod delete186Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = delete186Execute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod delete186func(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	do ..InitQms()
	new qqc186, result
	set qqc186 = qHandle(1)
	set result = qW.rDel(186,qqc186)
	set ^||result(1) = $LB(result)
}

Query cancel1860(qqc1860 As %String, reason As %String) As %Query(ROWSPEC = "qqc186:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod cancel1860Execute(ByRef qHandle As %Binary, qqc1860 = "", reason = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"cancel1860func",qqc1860,reason)
}

ClassMethod cancel1860Close(ByRef qHandle As %Binary) As %Status [ PlaceAfter = cancel1860Execute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod cancel1860Fetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = cancel1860Execute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod cancel1860func(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	set $zt = "cancel1860"
	
	new qqc1860,qqc186,reason,result,qqc1860Allstr,findAnother1860,index
	 
	set qqc1860 = qHandle(1)
	set reason = qHandle(2)
	set qqc186 = $E(qqc1860,1,19)
	do ..InitQMSqqc186(qqc186)
	set qqc174 = $E(qqc186,1,qW.ObjLget(174))
	// Если в эпизоде нет больше назначений кроме текущего то удалить 174 объект
	set qqc1860Allstr = qqc1860_" "_qW.FastKey(1860,"n","",1,qW.GG(186,"n",qqc186),qqc174)
	set findAnother1860=0
	set index = ""
	for{
		set index = qW.UserOrd(1,1860,index,qqc174)
		q:index=""
		if qqc1860Allstr '[ index set findAnother1860=1 quit
	}
	if findAnother1860{
		set result=qUSER.Ch1860(qqc1860,,,,reason)
	}
	else{
		do qW.rDel(174,qqc174)
		set result=""
	}
	set ^||result(1) = $LB(result)
	quit
cancel1860
	set ^||result(1) = $LB($ze)
}

/// Вход:
/// pIDo - код Организации
/// qqc244 - id Специалиста для которого нужно найти доступнных для назначения специалистов
/// Выход:
/// qqc244 - код найденног специалиста
/// specialization - специализация. Для ресурса кабинет возвращает "Кабинет"
/// firstName  - фамилия
/// lastName - Имя
/// middleName - отчество
Query AvailSpec(pIDo As %String, qqc244 As %String) As %Query(ROWSPEC = "qqc244:%String,specialization:%String,firstName:%String,lastName:%String,middleName:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod AvailSpecExecute(ByRef qHandle As %Binary, pIDo As %String = "", qqc244 As %String = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"AvailSpecfunc", pIDo, qqc244)
}

ClassMethod AvailSpecClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = AvailSpecExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod AvailSpecFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = AvailSpecExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod AvailSpecfunc(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new pIDo, qqc244spec, qqc244, index,index2, pID, pIDz, firstName, lastName, middleName, counter
	set $zt = "AvailSpecFunc"
	
	set qqc244spec = qHandle(2)
	set pIDo = qHandle(1)
	set counter = 0
	
	do ##class(tdv.Util).createQmsContext("ЗенковАЛ",,,0)
	
	set pIDList = qW.GG(244,"R0pID",qqc244spec) 
	set pIDzList = qW.GG(244,"R0pIDz",qqc244spec)
	if ((pIDList="")||(pIDzList=""))
	{
		set pIDList="", pIDzList=""
		set index=-1
		for{
			set index = $Order(^Q(1,244,qqc244spec,"Yptr",index))
			q:index=""
			set pIDList = $G(^Q(1,244,qqc244spec,"Yptr",index,"RspID"))
			set pIDzList = $G(^Q(1,244,qqc244spec,"Yptr",index,"RspIDz"))
			do addToResultFromPIDList()
		}
		
	}
	else{
		do addToResultFromPIDList()
	}
	quit
addToResultFromPIDList()	
	for index2=1:1{
		set pID = $P(pIDList, " ", index2)
		set pIDz = $P(pIDzList, " ", index2)
		q:((pID="")&&(pIDz=""))
		if ((pID="")||(pIDz="")) CONTINUE
		if (pID="*") set pID = qW.GG(244,"RSpID",qqc244spec)
		if (pIDz="*") set pIDz = qW.GG(244,"pIDz",qqc244spec)
		set qqc244 = qUSER.qqc244(pIDo, pID, pIDz)
		set spec = ..GetSpec(qqc244)
		if (spec="Кабинет"){
			set firstName = qW.GG(244,"pAz",qqc244)
			set middleName = ""
			set lastName = ""	
		}
		else{
			set firstName = $P(qW.GG(244,"pAz",qqc244),"_",1)
			set lastName = $P(qW.GG(244,"pAz",qqc244),"_",2)
			set middleName = $P(qW.GG(244,"pAz",qqc244),"_",3)
		}
		
		set ^||result(counter) = $LB(qqc244,spec,firstName,lastName,middleName) 
		set counter = counter + 1
	}
	quit 
AvailSpecFunc
	set ^||result(1)=$LB($ze,"")
}

Query LabServices(pIDo As %String, qqc244 As %String) As %Query(ROWSPEC = "code:%String,name:%String,lo:%String,container:%String, contingentRequired:%Boolean") [ SqlProc, WebMethod ]
{
}

ClassMethod LabServicesExecute(ByRef qHandle As %Binary, pIDo As %String, qqc244 As %String = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"LabServicesfunc",pIDo,qqc244)
}

ClassMethod LabServicesClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = LabServicesExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod LabServicesFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = LabServicesExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod LabServicesfunc(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new qqc83,qqc235,counter,qqc244,pIDo,MDu244,Du
	do ..InitQms()
	set pIDo = qHandle(1)
	set qqc244 = qHandle(2)
	set MDu244 = qW.GG(244,"MDu244",qqc244)
	set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"qW.G(""pIDo"")="""_pIDo_"""")
	set qqc83=""
	set counter=0
	for {
		set qqc83 = qW.FastKey(83,"tn pu",qqc83,1,"Лаборатория~Лабораторная_диагностика",qqc235)
		q:qqc83=""
		set Du = qW.GG(83,"Du",qqc83)
		if (MDu244=""||(MDu244[Du))
		set ^||result(counter) = $lb(Du,
									 qW.GG(83,"u",qqc83),
									 $Replace(qW.GG(83,"lo",qqc83),"|Y","*"),
									 qW.GG(83,"qlsLk",qqc83),
									 $S(qW.GG(83,"flgKO",qqc83)="":0,1:1))
		set counter=$i(counter)
	}
}

Query Lo(pIDo As %String) As %Query(ROWSPEC = "code:%String,name:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod LoExecute(ByRef qHandle As %Binary, pIDo As %String) As %Status
{
	quit ..GeneralExecute(.qHandle,"Lofunc",pIDo)
}

ClassMethod LoClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = LoExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod LoFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = LoExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod Lofunc(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	do ..InitQms()
	new lo,qqc235,counter
	set pIDo = qHandle(1)
	set ^CacheTampqZenk = pIDo
	set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"qW.G(""pIDo"")="""_pIDo_"""")
	set counter = 0
	set lo=""
	for {
		set lo = qW.UserOrd(1,"Lo",lo,qqc235)
		q:lo=""
		set ^||result(counter) = $LB(qW.GG("Lo","qlscodlo",lo),
									 qW.GG("Lo","qlslo",lo))
		set counter=$I(counter)								 
	}
}

Query RaspFree(qqc244 As %String, FromDate As %String, days As %String, fin As %String, info As %String, Du As %String) As %Query(ROWSPEC = "date:%String,dayslots:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod RaspFreeExecute(ByRef qHandle As %Binary, qqc244 As %String = "", FromDate As %String = "", days As %String = "", fin As %String = "", info As %String = "", Du As %String = "") As %Status [ Internal ]
{
	// look at %Library.Global for direct ^CacheTemp/^CacheTempNodes use with multi-row return possibility

	Set $zt="ERROR"
	If qqc244="" Quit $$$ERROR($$$InvalidParameter,"qqc244",qqc244)
	Set qHandle=""
	Set qHandle("qqc244")=qqc244
	Set qHandle("FromDate")=FromDate
	Set qHandle("days")=days
	Set qHandle("fin")=fin
	Set qHandle("info")=info
	Set qHandle("Du")=Du
		
	do ..getRaspFree(qqc244,FromDate,days,fin,info,Du)
	
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod RaspFreeFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = RaspFreeExecute ]
{
	Set $zt="ERROR"
	set ref = ..getRefRaspFree()
	
	Set idx=qHandle
	Set idx=$Order(@ref@(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=@ref@(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod RaspFreeClose(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = RaspFreeExecute ]
{
	
	set ref = ..getRefRaspFree("init")
	Quit $$$OK
}

ClassMethod getRefRaspFree(state As %String)
{
 set ref = $name(^||raspmainfree)
 if ($get(state) = "init") kill @ref
 
 quit ref
}

ClassMethod getRaspFree(qqc244 As %String, FromDate As %String, days As %String, fin As %String, info As %String, Du As %String) [ ProcedureBlock = 0 ]
{
 do ##class(tdv.Util).createQmsContext("ser",,,0) 
 S:fin'="" fin=" "_fin_" "
 S:info'="" info=" "_info_" "
 s:$G(days)<1 days=365
 D qZenk.QueryRasp(qqc244,FromDate,days)
 S i=0,str="",num=0,dateH=$ZDH(FromDate,8)
 S ref = ..getRefRaspFree("init")
 
 F day=1:1:days S date=dateH+day-1 D
 .Q:'$D(^||rasp(qqc244,day))
 .S dayslots=$P($P(^||rasp(qqc244,day),".",2),"~")-($P(^||rasp(qqc244,day),"."))
 .Q:dayslots<1
 .I (Du'="") || (info'="") || (fin'="") || (date=$P($H,",")) S str="",dayslots=0 D
 ..F  S str=$O(^||rasp(qqc244,day,str)) Q:str=""  D
 ...I date=$P($H,","),$ZTH($P(str,"-"))<$P($H,",",2) Q
 ...S Du1="",info1="",fin1=""
 ...S Du1=$P(^||rasp(qqc244,day,str),"~",4)
 ...S:Du1="" Du1=$P(^||rasp(qqc244,day),"~",4)
 ...S info1=$P(^||rasp(qqc244,day,str),"~",2)
 ...S:info1="" info1=$P(^||rasp(qqc244,day),"~",2)
 ...Q:($zcvt(info,"U")=" NULL ")&&(info1'="")
 ...S fin1=$P(^||rasp(qqc244,day,str),"~",11)
 ...S:fin1="" fin1=$P(^||rasp(qqc244,day),"~",11)
 ...Q:($zcvt(fin,"U")=" NULL ")&&(fin1'="")
 ...s Mr15=$P(^||rasp(qqc244,day,str),"~",14) ;@ser 20131230 Учитывается параметр Mr15 (Максимально допустимый интервал назначения (кол-во дней от текущей даты в течении которого возможно назначение))
 ...s:Mr15="" Mr15=$P(^||rasp(qqc244,day),"~",14)
 
 ...I $S(Mr15="":1,1:Mr15>=day), $S(Du'="":(Du1="" || ((" "_Du1_" ")[(" "_Du_" "))),1:1), $S($zcvt(info,"U")=" NULL ":1,info'="":(info1'=""&(info[(" "_info1_" "))),1:1), $S($zcvt(fin,"U")=" NULL ":1,fin'="":(fin1'=""&(fin[(" "_fin1_" "))),1:1) S dayslots=dayslots+($P($P(^||rasp(qqc244,day,str),".",2),"~")-($P(^||rasp(qqc244,day,str),".")))

 .I dayslots>0 D
 ..s @ref@(date) = $listBuild($ZD(date,8),dayslots)
 ..s i=$I(i)
 .S str="",info1="",Du1="",fin1=""
 ;M ^mtempR=^||rasp
 K ^||rasp
 quit
}

Query RaspFreeDetail(qqc244 As %String, FromDate As %String, fin As %String, info As %String, Du As %String, full As %String) As %Query(ROWSPEC = "str:%String,fin:%String,info:%String,cabinet:%String,Du:%String,status:%String,Max:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod RaspFreeDetailExecute(ByRef qHandle As %Binary, qqc244 As %String = "", FromDate As %String = "", fin As %String = "", info As %String = "", Du As %String = "", full As %String = "") As %Status [ Internal ]
{
	// look at %Library.Global for direct ^CacheTemp/^CacheTempNodes use with multi-row return possibility

	;Set $zt="ERROR"
	If qqc244="" Quit $$$ERROR($$$InvalidParameter,"qqc244",qqc244)
	Set qHandle=""
	Set qHandle("qqc244")=qqc244
	Set qHandle("FromDate")=FromDate
	Set qHandle("fin")=fin
	Set qHandle("info")=info
	Set qHandle("Du")=Du
	Set qHandle("full")=full
		
	do ..getRaspFreeDetail(qqc244,FromDate,fin,info,Du,full)
	
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod RaspFreeDetailFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = RaspFreeDetailExecute ]
{
	;Set $zt="ERROR"
	set ref = ..getRefRaspFreeDetail()
	
	Set idx=qHandle
	Set idx=$Order(@ref@(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=@ref@(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod RaspFreeDetailClose(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = RaspFreeDetailExecute ]
{
	
	set ref = ..getRefRaspFreeDetail("init")
	Quit $$$OK
}

ClassMethod getRefRaspFreeDetail(state As %String)
{
 set ref = $name(^||raspmainfreedetail)
 if ($get(state) = "init") kill @ref
 
 quit ref
}

ClassMethod getRaspFreeDetail(qqc244 As %String, FromDate As %String, fin As %String, info As %String, Du As %String, full As %String) [ ProcedureBlock = 0 ]
{
 do ##class(tdv.Util).createQmsContext("ser",,,0)
 s qqred=""
 S:fin'="" fin=" "_fin_" "
 S:info'="" info=" "_info_" "
 s qEXP=##class(User.qEXP).%New()
 D qZenk.QueryRasp(qqc244,FromDate,1)
 
 S str="",num=0, logStr=""
 
 S full=$G(full,0)
 S status=""
 		
 S ref = ..getRefRaspFreeDetail("init")
 S day=1
 F  S str=$O(^||rasp(qqc244,day,str)) Q:str=""  D
 .S:full status=1
 .I $S($P(^||rasp(qqc244,day,str),".")<$P($P(^||rasp(qqc244,day,str),"~"),".",2):0,1:1) Q:'full  S status=0
 .;Q:($S($P(^||rasp(qqc244,day,str),".")<$P($P(^||rasp(qqc244,day,str),"~"),".",2):0,1:1))
 .S info1=$P(^||rasp(qqc244,day,str),"~",2)
 .S Du1=$P(^||rasp(qqc244,day,str),"~",4)
 .S fin1=$P(^||rasp(qqc244,day,str),"~",11)
 .S:info1="" info1=$P(^||rasp(qqc244,day),"~",2)
 .S:Du1="" Du1=$P(^||rasp(qqc244,day),"~",4)
 .S:fin1="" fin1=$P(^||rasp(qqc244,day),"~",11)
 .I info'="",info1="" || (info'[(" "_info1_" ")) Q
 .I Du'="",$S(Du1="":0,1:((" "_Du1_" ")'[(" "_Du_" "))) Q
 .I fin'="",fin1="" || (fin'[(" "_fin1_" ")) Q
 .;S max=$P(^||rasp(qqc244,day,str),"~",5)
 .S cabinet=$P(^||rasp(qqc244,day,str),"~",3)
 .S:cabinet="" cabinet=$P(^||rasp(qqc244,day),"~",3)
 .S:cabinet="" cabinet=qW.GG(244,"pMO",qqc244)
 .s Mr15=$P(^||rasp(qqc244,day,str),"~",14) ;@ser 20131230 Учитывается параметр Mr15 (Максимально допустимый интервал назначения (кол-во дней от текущей даты в течении которого возможно назначение))
 .s:Mr15="" Mr15=$P(^||rasp(qqc244,day),"~",14)
 .; 
 .S logStr=logStr_$C(13,10)_str_" "_fin1_" "_info1_" "_Du1_" "_status
 .;
 .set @ref@(str) = $listBuild(str,fin1,info1,cabinet,Du1,status,Mr15)
 .S info1="",Du1="",cabinet="",fin1="",max="",status=""
 
 ;S ^QMSlog("Query.RaspFreeDetail",$P($ZDT($H,8)," "),$P($ZDT($H,8)," ",2),$P($ZH,".",2))="qqc244="_qqc244_" | date="_FromDate_" | slots:"_logStr 
 
 K ^||rasp
 
 quit
}

/// CrePolis в виде Query 
/// Org - организация 
/// qqc153 - код экземпляра пациента
/// pB - рег. номер СМО из GetSMO("Образец","название региона")
/// pIDo - имя организации в, которой хранится СМО из GetSMO("Образец","название региона")
/// tpl - тип плательщика по умолчанию ОМС
/// pU - серия полиса
/// pV - номер полиса
/// pW - дата начала действия полиса (ГГГГММДД)
/// td - тип документа из GetVoc("Образец","td","ОМС")
/// fio - наименование СМО из GetSMO("Образец","название региона")
/// pN - наименование региона для определения ОКАТО из GetVoc("Образец",pN)
/// возвращает:
///  - код экземпляра созданного полиса
///  0 - если полис не создан
Query CrePolisQuery(Org As %String, qqc153 As %String, pB As %String, pIDo As %String, tpl As %String = "ОМС", pU As %String, pV As %String, pW As %String, td As %String, fio As %String, pN As %String) As %Query(ROWSPEC = "qqc1600:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod CrePolisQueryExecute(ByRef qHandle As %Binary, Org As %String, qqc153 As %String, pB As %String, pIDo As %String, tpl As %String, pU As %String, pV As %String, pW As %String, td As %String, fio As %String, pN As %String) As %Status [ Internal ]
{
	// look at %Library.Global for direct ^CacheTemp/^CacheTempNodes use with multi-row return possibility
	
	Set $zt="ERROR"
	If Org="" Quit $$$ERROR($$$InvalidParameter,"Org",Org)
	Set qHandle=""
	Set qHandle("Org")=Org
	Set qHandle("qqc153")=qqc153
	Set qHandle("pB")=pB
	Set qHandle("pIDo")=pIDo
	Set qHandle("pW")=pW
	Set qHandle("td")=td
	Set qHandle("tpl")=tpl
	Set qHandle("pU")=pU
	Set qHandle("pV")=pV
	Set qHandle("fio")=fio
	Set qHandle("pN")=pN
		
	do ..getCrePolisQueryList(Org, qqc153, pB,pIDo,tpl, pU, pV,pW, td, fio, pN)
	
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod CrePolisQueryFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = CrePolisQueryExecute ]
{
	Set $zt="ERROR"
	set ref = ..getRefCrePolisQuery()
	
	Set idx=qHandle
	Set idx=$Order(@ref@(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=@ref@(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod CrePolisQueryClose(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = CrePolisQueryExecute ]
{
	
	set ref = ..getRefCrePolisQuery("init")
	Quit $$$OK
}

ClassMethod getRefCrePolisQuery(state As %String)
{
 set ref = $name(^||CrePolisQuery)
 if ($get(state) = "init") kill @ref
 
 quit ref
}

ClassMethod getCrePolisQueryList(Org As %String, qqc153 As %String, pB As %String, pIDo As %String, tpl As %String, pU As %String, pV As %String, pW As %String, td As %String, fio As %String, pN As %String) [ ProcedureBlock = 0 ]
{
 do ##class(tdv.Util).createQmsContext("ser",,,0) 
 S ref = ..getRefCrePolisQuery("init")
 
 s qqc1600=$S(qW.UserOrd(-1,1600,,qqc153)'="":qW.UserOrd(-1,1600,,qqc153,,qW.zTmpI(1,,,1600,qW.UserOrd(-1,1600,,qqc153))),1:"")
 
 i (qW.GG(1600,"fio",qqc1600)_qW.GG(1600,"pV",qqc1600))'=(fio_pV) {
 S qqc1600=qZenk.QueryCrePolis(Org, qqc153, pB,pIDo,tpl, pU, pV,pW, td, fio, pN)
 ;S ^QMSlog("Query.CrePolisQuery",$P($ZDT($H,8)," "),$P($ZDT($H,8)," ",2),$P($ZH,".",2))="status=полис записан для qqc153="_qqc153_" | СМО="_fio_" | номер="_pV
 }
 else {s qqc1600="0"
 ;S ^QMSlog("Query.CrePolisQuery",$P($ZDT($H,8)," "),$P($ZDT($H,8)," ",2),$P($ZH,".",2))="status=полис не записан для qqc153="_qqc153_" | СМО="_fio_" | номер="_pV
 }
 set @ref@(1) = $listBuild(qqc1600) 
 
 quit
}

/// Org - код организации (pIDo)
/// pN - имя региона
/// возвращает: 
/// fio - наименование СМО
/// pB - рег. номер СМО 
/// pIDo - имя организации в, которой хранится СМО
Query GetSMO(Org As %String, pN As %String) As %Query(ROWSPEC = "fio:%String,pB:%String,pIDo:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod getRefGetSMO(state As %String)
{
 set ref = $name(^||GetSMO)
 if ($get(state) = "init") kill @ref
 
 quit ref
}

ClassMethod GetSMOClose(ByRef qHandle As %Binary) As %Status [ Internal, PlaceAfter = GetSMOExecute ]
{
	set ref = ..getRefGetSMO("init")
	Quit $$$OK
}

ClassMethod GetSMOExecute(ByRef qHandle As %Binary, Org As %String = "", pN As %String) As %Status [ Internal ]
{
	// look at %Library.Global for direct ^CacheTemp/^CacheTempNodes use with multi-row return possibility

	Set $zt="ERROR"
	If Org="" Quit $$$ERROR($$$InvalidParameter,"Org",Org)
	Set qHandle=""
	Set qHandle("Org")=Org
	Set qHandle("pN")=pN
		
	do ..GetlistSMO(Org,pN)
	
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod GetSMOFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ Internal, PlaceAfter = GetSMOExecute ]
{
	Set $zt="ERROR"
	set ref = ..getRefGetSMO()
	
	Set idx=qHandle
	Set idx=$Order(@ref@(idx))
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0,Row=@ref@(idx)
	}
	
	Set qHandle=idx
	Quit $$$OK
ERROR
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

/// Метод записывает в массив данные по указанному региону.
/// Org - код организации (pIDo)
/// pN - имя региона
ClassMethod GetlistSMO(Org As %String, pN As %String) [ ProcedureBlock = 0 ]
{
	S ref = ..getRefGetSMO("init")
	if '$D(^Q(1,"pN",pN)) Q
	set ID=$O(^Q(1,"pN",pN,"ww",""))
 	do ##class(User.qZenk.qZenk).getSMOList(Org,ID,"vABdAAHACAJ")
 	//^||CacheTempANK(18142,"SMOoms",
 	set index=""
 	for{
 		set index = $O(^||CacheTempANK($J,"SMOoms",index))
 		q:index=""
 		if $G(^||CacheTempANK($J,"SMOoms",index,"DEL"))'=1{
 			
            set @ref@(index)=$listBuild($G(^||CacheTempANK($J,"SMOoms",index,"a")),     						  
            						  $G(^||CacheTempANK($J,"SMOoms",index,"b")),
            						  $G(^||CacheTempANK($J,"SMOoms",index,"c")))
 		}
 	}
 	Q
}

/// Возвращает всех врачей в подразделении организации
/// Вход:
/// pIDo - код организации
/// pID - код отделения. Если не задан то на выходе все врачи в организации
/// Выход:
/// qqc244 - код найденног специалиста
/// specialization - специализация. Для ресурса кабинет возвращает "Кабинет"
/// firstName  - фамилия
/// lastName - Имя
/// middleName - отчество 
Query Doctors(pIDo As %String, pID As %String) As %Query(ROWSPEC = "qqc244:%String,specialization:%String,firstName:%String,lastName:%String,middleName:%String,IsActive:%Boolean") [ SqlProc, WebMethod ]
{
}

ClassMethod DoctorsExecute(ByRef qHandle As %Binary, pIDo = "", pID = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"getDoctors",pIDo,pID)
}

ClassMethod DoctorsClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = DoctorsExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod DoctorsFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = DoctorsExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getDoctors(ByRef qHandle) [ ProcedureBlock = 0 ]
{
	new pIDo,pID,qqc153InList,qqc153List,index, spec, firstName, lastName, middleName
	do ..InitQms()
	set pIDo = qHandle(1)
	set pID = qHandle(2)
	set qqc153List = qUSER.qqc153dep(qUSER.qqc153org(pIDo,pID),2)
	set qqc153InList = ""
	for index = 1:1{
		set qqc153InList = $P(qqc153List," ",index) q:qqc153InList=""
		do AddSpecsForDep(qW.GG(153,"pID",qqc153InList)) 
	}
AddSpecsForDep(pID)
	new qqc244
	set qqc244 ="" 
	for{
		set qqc244 = $Order(^Q(1,"pID",pID,244,qqc244)) 
		q:qqc244=""
		// Добавление ресурса в массив с результатами если ресурс Специалист или Кабинет
		if (($Data(^Q(1,"pID",pID,244,qqc244,"S"))'=0)&&
			($$IsDoctor(qqc244)||$$IsCabinet(qqc244))){
				set spec = ..GetSpec(qqc244)
				if (spec="Кабинет"){
					set firstName = $Replace(qW.GG(244,"pAz",qqc244),"_"," ")
					set middleName = ""
					set lastName = ""	
				}
				else{
					set firstName = $P(qW.GG(244,"pAz",qqc244),"_",1)
					set lastName = $P(qW.GG(244,"pAz",qqc244),"_",2)
					set middleName = $P(qW.GG(244,"pAz",qqc244),"_",3)
				} 
				set ^||result(qqc244) = $LB(qqc244,spec,
										firstName,
										lastName,
										middleName,
										qW.zTmpI(1,,,244,qqc244))
		}
	}			
	quit
 //Возвращает 1 если ресурс имеет медецинскую специальность 
 //и не является младшим и средним медецинским персоналом
 
IsDoctor(qqc244)
	quit ((qW.GG("nSpec","nSpec0:n611",qW.FastKey("nSpec","n647","",1,qW.GG(244,"n647",qqc244)))="ЗДРАВООХРАНЕНИЕ")&& 
		  (qW.GG(244,"@puR.t",qqc244)'="Средний_медицинский_персонал")&&
		  (qW.GG(244,"@puR.t",qqc244)'="Младший_медицинский_персонал"))
IsCabinet(qqc244)
	quit qW.GG(244,"@puR.t",qqc244)="Кабинет"
}

// =====================Загрузка справосника ОКМУ===========================================

Query OKMU(pIDo As %String, level As %String) As %Query(ROWSPEC = "code:%String,name:%String,parent:%String,type:%String,settings:%String") [ SqlProc ]
{
}

ClassMethod OKMUExecute(ByRef qHandle As %Binary, pIDo As %String, level As %Integer) As %Status [ ProcedureBlock = 0 ]
{
	Set $zt="ERROREXOKMU"
	Set qHandle=""
	set qHandle(1) = $Case(level,1:80,2:81,3:82,4:83,:0)
	set qHandle(2) = pIDo
	do ..InitQms()
	Quit $$$OK
ERROREXOKMU
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod OKMUClose(ByRef qHandle As %Binary) As %Status
{
	Quit $$$OK
}

ClassMethod OKMUFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ ProcedureBlock = 0 ]
{
	if ($D(qW)=0) do ..InitQms()
	Set $zt="ERRORFETOKMU"
	Set idx=qHandle
	set pIDo = qHandle(2)
	set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"qW.G(""pIDo"")="""_pIDo_"""")

next	
	Set idx=qW.UserOrd(1,qHandle(1),idx,qqc235)
	if ('$$HasChild()) goto next
	if (idx = "") {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0
		set Row=..getOKMURow(idx,qHandle(1))
	}
	
	Set qHandle=idx
	Quit $$$OK
ERRORFETOKMU
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
HasChild()
	if (qHandle(1)<83){
		if (qW.UserOrd(1,qHandle(1)+1,"",idx)="") quit 0
		quit 1
	}
	quit 1
}

ClassMethod getOKMURow(index, obj) As %List [ ProcedureBlock = 0 ]
{

	if ($D(qW)=0) do ..InitQms()
	set parentObj = obj-1
	set parentCode = ""
	if (obj > 80) {
		set pidx = $Extract(index,1,qW.ObjLget(parentObj))
		set parentCode = qW.GG(parentObj,"Du",pidx)
	}
	set tn = qW.GG(obj,"tn",index)
	k ^||settings
	if tn="Лаборатория"{
		set ^||settings("lab_speciman") = $Replace(qW.GG(obj,"lo",index),"|Y","*")
		set ^||settings("cl_lab_condition") = qW.GG(obj,"qlsLk",index)
		set ^||settings("contingent_flag") = $S(qW.GG(obj,"flgKO",index)="":0,1:1)
	}
	
	quit $LB(qW.GG(obj,"Du",index),
			 $Replace(qW.GG(obj,"u",index),"_"," "),
			 parentCode,
			 tn,
			 ##class(Util.JSON).encode($Name(^||settings))
    
	)
}

// =====================Загрузка справосника MKB===========================================

/// Загрузка справочника MKB 
Query MKB(level As %String) As %Query(ROWSPEC = "code:%String,name:%String,parent:%String") [ SqlProc ]
{
}

ClassMethod MKBExecute(ByRef qHandle As %Binary, level As %Integer) As %Status [ ProcedureBlock = 0 ]
{
	Set $zt="ERROREXMKB"
	Set qHandle=""
	set qHandle(1) = level
	do ..InitQms()
	Quit $$$OK
ERROREXMKB
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
	Quit $$$OK
}

ClassMethod MKBClose(ByRef qHandle As %Binary) As %Status [ ProcedureBlock = 0 ]
{
	Quit $$$OK
}

ClassMethod MKBFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ ProcedureBlock = 0 ]
{
	if ($D(qW)=0) do ..InitQms()
	Set $zt="ERRORFETMKB"
	Set idx=qHandle

	Set idx=qW.UserOrd(1,qHandle(1),idx)
	if ((idx = "")||(qW.GG(qHandle(1),"rub",idx)="")) {
		set AtEnd=1,Row=""
	}
	else {
		set AtEnd=0
		set Row=..getMKBRow(idx,qHandle(1))
	}
	
	Set qHandle=idx
	Quit $$$OK
ERRORFETMKB
	Set $zt="" Quit $$$ERROR($$$CacheError,$ze)
}

ClassMethod getMKBRow(index, obj) As %List [ ProcedureBlock = 0 ]
{

	if ($D(qW)=0) do ..InitQms()
	set parentObj = obj-1
	set pidx = $Extract(index,1,qW.ObjLget(parentObj))
	set parentCode = qW.GG(parentObj,"rub",pidx)
	quit $LB(qW.GG(obj,"rub",index),
			 qW.GG(obj,"z",index),
			 parentCode
	)
}

Query Tses(pIDo As %String) As %Query(ROWSPEC = "name:%String,color:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod TsesExecute(ByRef qHandle As %Binary, pIDo = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"getTses",pIDo)
}

ClassMethod TsesClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = TsesExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod TsesFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = TsesExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getTses(ByRef qHandle) [ ProcedureBlock = 0 ]
{
    set pIDo = $G(qHandle(1))
    if ($D(qW)=0) do ..InitQms()
    set qqc235 = qW.FastKey(235,"pIDo","",1,pIDo,,,,"NR")
    set qqcw = qW.FastKey("w","DxWoc","",1,"tses",qqc235)
    set qqcww=""
    for{
    	s qqcww= qW.UserOrd(1,"ww",qqcww,qqcw) q:qqcww=""
    	set color = qW.GG("ww","M0tses",qqcww)
    	if color'=""
    	{
	    	set color=$ZH(color)
	    	set color=$Replace($justify(color,6)," ",0)
	    	set color = "#"_$E(color,5,6)_$E(color,3,4)_$E(color,1,2)
    	}
    	s ^||result(qqcww) = $LB(qW.GG("ww","tses",qqcww),color)
    }
}

Query SpecialistPerformingServices(qqc244 As %String) As %Query(ROWSPEC = "code:%String") [ SqlProc, WebMethod ]
{
}

ClassMethod SpecialistPerformingServicesExecute(ByRef qHandle As %Binary, qqc244 = "") As %Status
{
	quit ..GeneralExecute(.qHandle,"getSpecialistPerformingServices",qqc244)
}

ClassMethod SpecialistPerformingServicesClose(ByRef qHandle As %Binary) As %Status [ PlaceAfter = SpecialistPerformingServicesExecute ]
{
	quit ..GeneralClose(.qHandle)
}

ClassMethod SpecialistPerformingServicesFetch(ByRef qHandle As %Binary, ByRef Row As %List, ByRef AtEnd As %Integer = 0) As %Status [ PlaceAfter = SpecialistPerformingServicesExecute ]
{
	quit ..GeneralFetch(.qHandle,.Row,.AtEnd)
}

ClassMethod getSpecialistPerformingServices(ByRef qHandle) [ ProcedureBlock = 0 ]
{
    set qqc244 = $G(qHandle(1))
    if ($D(qW)=0) do ..InitQms()
    
    set Du = qW.GG(244,"Du",qqc244)
    for i=1:1:$length(Du," ")
    {
        set ^||result(i)= $LB($P(Du," ",i))
    }
}

}

