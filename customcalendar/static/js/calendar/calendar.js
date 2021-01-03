class CalendarData{
    static object = undefined;

    constructor(id=undefined, link=undefined, containerControls=undefined, containerCalendar=undefined, 
        curdatesetup=undefined, eventslink=undefined, curdatelink=undefined){
        this._id = id;
        this._submitlink = link;
        this._eventsLink = eventslink;
        this._updateCurDateLink = curdatelink;
        this._containerControls = containerControls;
        this._containerCalendar = containerCalendar;
        this._curDateSetup = curdatesetup;
        this._currentDate = undefined;
        this._months = [];
        this._weekdays = [];
        this._yearTables = {};
        this._events = {};
        this._redirect = false;
        var res = /(\d+)(-(\d+))?(-(\d+))?/.exec(window.location.hash);
        if ((res != null) && (res != undefined) && (res[1]!==undefined)){
            var day = res[5];
            if (day === undefined){
                day = 1;
            }
            else{
                day = parseInt(day);
            }
            var month = res[3];
            if (month === undefined){
                month = 1;
            }
            else{
                month = parseInt(month);
            }
            var year = parseInt(res[1]);
            this._currentDate = [day, month, year];
            this._redirect = true;
        }
    }

    get ID(){
        return this._id;
    }

    get firstYear(){
        if (this._firstyear === undefined){
            return 0;
        }
        return this._firstyear;
    }

    get daysInYear(){
        if (this._daysInYear === undefined){
            var result = 0;
            for(var i=0; i<this._months.length; i++){
                result += this._months[i].NumberOfDays;
            }
            if (result>0){
                this._daysInYear = result;
            }
            return result;
        }
        else{
            return this._daysInYear;
        }
    }

    get weekDays(){
        return this._weekdays.length;
    }

    get currentDate(){
        if (this._currentDate === undefined){
            return [1, 1, 0];
        }
        return [this._currentDate[0], this._currentDate[1], this._currentDate[2]];
    }

    get submitLink(){
        if (this._submitlink === undefined){
            return window.location.pathname + '/general';
        }
        return this._submitlink;
    }

    get Editable(){
        if (this._editable === undefined){
            return false;
        }
        return this._editable;
    }

    get UpdateCurDateLink(){
        if (this._updateCurDateLink === undefined){
            return window.location.pathname + '/date/update';
        }
        return this._updateCurDateLink;
    }

    get DateHash(){
        var date = this.currentDate;
        return date[2].toString() + '-' + date[1].toString() + '-' + date[0].toString(); 
    }

    get Redirect(){
        if (this._redirect === undefined){
            return false;
        }
        return this._redirect;
    }

    getEventsLink(year){
        if (this._eventsLink !== undefined){
            return this._eventsLink.replace('<year>', year.toString());
        }
        if (window.location.pathname.endsWith('/')){
            return window.location.pathname + 'events/' + year.toString(); 
        }
        return window.location.pathname + '/events/' + year.toString(); 
    }

    getMonth(monthnumber){
        if(this._months.length > monthnumber){
            return this._months[monthnumber-1];
        }
        else{
            return undefined;
        }
    }
    
    setCurrentDate(day, month, year){
        this._currentDate = this.FixDate([day, month, year]);
        this.CurDateForm;
    }

    daysFromStartOfYear(date){
        if (date.length==3){
            if (date[1]>this._months.length){
                return undefined;
            }
            var result = date[0]-1;
            for(var i=0; i<date[1]-1; i++){
                result+=this._months[i].NumberOfDays;
            }
            return result;
        }
        return undefined;
    }

    dayOfWeek(date){
        if (this._weekdays.length == 0){
            return undefined;
        }
        if (date[2]>=this._firstyear){
            var result = this.daysFromStartOfYear(date)+(date[2]-this._firstyear)*this.daysInYear;
            result = result % this.weekDays;
            return this._weekdays[result];
        }
        else{
            var result = this.daysFromStartOfYear(date)+(date[2]-this._firstyear)*this.daysInYear;
            result = Math.abs(result) % this.weekDays;
            return this._weekdays[(this.weekDays - result)% this.weekDays];
        }
    }

    static fromDictionary(dict, link=undefined){
        result = new CalendarData(undefined, undefined, link);
        result.updateDataDictionary(dict);
    }

    get jsonData(){
        result = {
            'targetid': this.ID, 
            'firstyear': this.firstYear, 
            'action':'changed'
        };
        return result;
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._firstyear = dict['firstyear'];
        this._daysInYear = dict['dpy'];
        this._editable = dict['editable'];
        
        if (('curday' in dict) && ('curmonth' in dict) && ('curyear' in dict)){
            if (this._currentDate === undefined){
                this._currentDate = [dict['curday'], dict['curmonth'], dict['curyear']];
            }
        }
        if ('months' in dict){
            this.updateDataDictionaryMonths(dict['months']);
        }
        if ('week' in dict){
            if ('days' in dict['week']){
                this.updateDataDictionaryWeekDays(dict['week']['days']);
            }
        }
    }

    updateDataDictionaryWeekDays(list){
        if (list === undefined)
            return;
        for(var i=0; i<list.length; i++){
            var newday = true;
            for(var j=0; j<this._weekdays.length; j++){
                if (this._weekdays[j].ID == list[i]['id']){
                    this._weekdays[j].updateDataDictionary(list[i]);
                    newday = false;
                }
            }
            if (newday){
                this._weekdays.push(CalendarWeekDay.fromDictionary(list[i]));
            }
        }
    }

    updateDataDictionaryMonths(list){
        if (list === undefined)
            return;
        for(var i=0; i<list.length; i++){
            var newmonth = true;
            for(var j=0; j<this._months.length; j++){
                if (this._months[j].ID == list[i]['id']){
                    this._months[j].updateDataDictionary(list[i]);
                    newmonth = false;
                }
            }
            if (newmonth){
                this._months.push(CalendarMonth.fromDictionary(list[i]));
            }
        }
    }

    updateFromAjax(requestLink = undefined){
        if (requestLink === undefined)
            requestLink = this.submitLink;
        document.calData = this;
        sendGetAjax(requestLink, undefined, 
            function(data, status){
                document.calData.updateDataDictionary(data['calendar']);
                document.calData.fillContainers();
            },
            function(data, status){
                console.log(data);
            },
            false,
            this
        );
    }

    parseEventsForYear(events){
        for(var i=0; i<events.length; ++i){
            var event = CalendarEvent.fromDictionary(events[i]);
            if (!(event.Year in this._events)){
                this._events[event.Year] = {};
            }
            if (!(event.Month in this._events[event.Year])){
                this._events[event.Year][event.Month] = {};
            }
            if (!(event.Day in this._events[event.Year][event.Month])){
                this._events[event.Year][event.Month][event.Day] = [];
            }
            this._events[event.Year][event.Month][event.Day].push(event);
        }
    }

    getEventsForYear(year){
        if (year in this._events){
            return this._events[year];
        }
        this._loading = true;
        this._events[year] = {};
        sendGetAjax(this.getEventsLink(year), undefined, function(data, status){
            this.parseEventsForYear(data['events']);
            this._loading = false;
        },
        function(data, status){
            console.log(data);
            this._loading = false;
        }, false, this);
        return this._events[year];
    }

    UpdateCurrentDate(day, month, year){
        var date = this.FixDate([day, month, year]);
        var data = {
            'currentday': date[0],
            'currentmonth': date[1],
            'currentyear': date[2],
            'targetid':this.ID,
            'action':'changed' 
        };
        this.ChangeCurDateForm.day.value = date[0];
        this.ChangeCurDateForm.month.value = date[1];
        this.ChangeCurDateForm.year.value = date[2];
        sendPostAjax(this.UpdateCurDateLink, data, function(data, status){
            this.ChangeCurDateForm.submButton.classList.remove('alert');
            this.ChangeCurDateForm.submButton.classList.add('success');
        },
        function(data, status){
            this.ChangeCurDateForm.submButton.classList.add('alert');
            this.ChangeCurDateForm.submButton.classList.remove('success');
            console.log(data);
        }, true, this);
    }

    createViewForOneMonth(date, firstday){
        var events = {};
        if (date[1] in this._events[date[2]]){
            events = this._events[date[2]][date[1]];
        }
        var wrapper = document.createElement('div');
        wrapper.classList.add('calendar-wrapper');
        var header = document.createElement('h4');
        var montha = document.createElement('a');
        montha.id= date[2].toString() + '-' + date[1].toString();
        montha.href= '#' + date[2].toString() + '-' + date[1].toString();
        montha.innerText = this._months[date[1]-1].Name+' '+date[2].toString();
        if (this.Redirect){
            if ((date[2] == this.currentDate[2]) && (date[1] == this.currentDate[1])){
                this._redirectTarget = montha;
            }
        }
        header.appendChild(montha);
        wrapper.appendChild(header);
        var calendarList = document.createElement('ol');
        calendarList.classList.add('calendar');
        calendarList.style.gridTemplateColumns = 'repeat('+this.weekDays.toString()+', 1fr)';
        for(var i=0; i<this._weekdays.length; i++){
            var day = document.createElement('li');
            day.innerText = this._weekdays[i].Name;
            day.classList.add('calendar-daynames')
            calendarList.appendChild(day);
        }
        for(var i=0; i<this._months[date[1]-1].NumberOfDays; i++){
            var day = document.createElement('li');
            day.classList.add('calendar-day');
            var daya = document.createElement('a');
            daya.id= date[2].toString() + '-' + date[1].toString() + '-' + (i+1).toString();
            day.innerText = (i+1).toString();
            day.appendChild(daya);
            if ((i+1) in events){
                for (var j=0; j<events[i+1].length; j++){
                    day.appendChild(events[i+1][j].EventLinkElement);
                }
            }
            if (i==0){
                day.style.gridColumnStart = firstday.DayNumber;
            }
            calendarList.appendChild(day);
        }
        wrapper.appendChild(calendarList);
        return wrapper;
    }

    get MonthTables(){
        var date = this.currentDate;
        if (this._currentTable !== undefined){
            this._currentTable.classList.add('is-hidden');
        }
        if (date[2] in this._yearTables){
            this._currentTable = this._yearTables[date[2]];
            this._currentTable.classList.remove('is-hidden');
            return this._currentTable;
        }
        this.getEventsForYear(date[2]);
        var result = document.createElement('div');
        for(var i=1; i<=this._months.length; i++){
            var tmp = [1, i, date[2]];
            result.appendChild(this.createViewForOneMonth(tmp, this.dayOfWeek(tmp)));
        }
        this._yearTables[date[2]] = result;
        this._currentTable = result;
        this._containerCalendar.appendChild(result);
        return result;
    }

    get CurDateForm(){
        if (this._curDateForm===undefined){
            var form = document.createElement('form');
            form.classList.add('calendar-controller-form');
            var dayInput = document.createElement('input');
            dayInput.type = 'number';
            form.appendChild(dayInput);
            form.day = dayInput;
            var span = document.createElement('span');
            span.innerText = '—';
            form.appendChild(span);

            var monthInput = document.createElement('select');
            for (var i=0; i<this._months.length; i++){
                var monthOption = document.createElement('option');
                monthOption.value = this._months[i].MonthNumber;
                monthOption.data = this._months[i];
                monthOption.innerText = this._months[i].Name;
                monthInput.appendChild(monthOption);
            }
            form.appendChild(monthInput);
            form.month = monthInput;
            var span = document.createElement('span');
            span.innerText = '—';
            form.appendChild(span);

            var yearInput = document.createElement('input');
            yearInput.type = 'number';
            form.appendChild(yearInput);
            form.year = yearInput;
            this._curDateForm = form;

            var submitButton = document.createElement('button');
            submitButton.classList.add('button', 'round');
            submitButton.innerText = 'Go to date';
            submitButton.onclick = function(){
                document.calData.setCurrentDate(document.calData._curDateForm.day.value, 
                document.calData._curDateForm.month.value, document.calData._curDateForm.year.value);
                document.calData.fillContainers();
                window.location.hash = document.calData.DateHash;
                return false;
            };
            form.appendChild(submitButton);
        }
        var date = this.currentDate;
        this._curDateForm.day.value = date[0];
        this._curDateForm.month.value = date[1];
        this._curDateForm.year.value = date[2];
        return this._curDateForm;
    }

    get ChangeCurDateForm(){
        if (this._changeCurDate===undefined){
            var form = document.createElement('form');
            form.classList.add('calendar-controller-form');
            var dayInput = document.createElement('input');
            dayInput.type = 'number';
            form.appendChild(dayInput);
            form.day = dayInput;
            var span = document.createElement('span');
            span.innerText = '—';
            form.appendChild(span);

            var monthInput = document.createElement('select');
            for (var i=0; i<this._months.length; i++){
                var monthOption = document.createElement('option');
                monthOption.value = this._months[i].MonthNumber;
                monthOption.data = this._months[i];
                monthOption.innerText = this._months[i].Name;
                monthInput.appendChild(monthOption);
            }
            form.appendChild(monthInput);
            form.month = monthInput;
            var span = document.createElement('span');
            span.innerText = '—';
            form.appendChild(span);

            var yearInput = document.createElement('input');
            yearInput.type = 'number';
            form.appendChild(yearInput);
            form.year = yearInput;
            this._changeCurDate = form;

            var submitButton = document.createElement('button');
            submitButton.classList.add('button', 'round');
            submitButton.innerText = 'Update current date';
            submitButton.onclick = function(){
                document.calData.UpdateCurrentDate(document.calData._changeCurDate.day.value, 
                document.calData._changeCurDate.month.value, document.calData._changeCurDate.year.value);
                return false;
            };
            form.appendChild(submitButton);
            form.submButton = submitButton;
            var date = this.currentDate;
            this._changeCurDate.day.value = date[0];
            this._changeCurDate.month.value = date[1];
            this._changeCurDate.year.value = date[2];
        }
        return this._changeCurDate;
    }

    get ControlsCurDate(){
        if (this._controlsWrapper !== undefined){
            return this._controlsWrapper;
        }
        var wrapper = document.createElement('div');
        wrapper.classList.add('row');
        var leftpart = document.createElement('div');
        leftpart.classList.add('column', 'centered-element');
        var prevyear = document.createElement('a');
        prevyear.classList.add('button', 'round');
        prevyear.innerText = 'Previous year';
        prevyear.onclick = function(){
            var date = document.calData.currentDate;
            document.calData.setCurrentDate(date[0], date[1], date[2]-1);
            document.calData.fillContainers();
        }
        leftpart.appendChild(prevyear);
        wrapper.appendChild(leftpart);

        var middlepart = document.createElement('div');
        middlepart.classList.add('column', 'centered-element');
        middlepart.appendChild(this.CurDateForm);
        wrapper.appendChild(middlepart);

        var rightpart = document.createElement('div');
        rightpart.classList.add('column', 'centered-element');
        var nextyear = document.createElement('a');
        nextyear.innerText = 'Next year';
        nextyear.classList.add('button', 'round');
        nextyear.onclick = function(){
            var date = document.calData.currentDate;
            document.calData.setCurrentDate(date[0], date[1], date[2]+1);
            document.calData.fillContainers();
        }
        rightpart.appendChild(nextyear);
        wrapper.appendChild(rightpart);


        this._controlsWrapper = wrapper;
        return wrapper;
    }

    FixMonth(date){
        if (date.length<3){
            return undefined;
        }
        if (this._months.length<1){
            return date;
        }
        if (date[1]<=0){
            date[2] -= 1;
            date[1] = this._months.length + date[1];
            return this.FixMonth(date);
        }
        if (date[1] > this._months.length){
            date[2] += 1;
            date[1] = date[1] - this._months.length;
            return this.FixMonth(date);
        }
        return date;
    }

    FixDate(date){
        if (date.length<3)
            return undefined;
        if (this._months.length<1){
            return date;
        }
        if (date[0]<=0){
            date[1] -= 1;
            date = this.FixMonth(date);
            date[0] += this._months[date[1]-1].NumberOfDays;
            return this.FixDate(date);
        }
        date = this.FixMonth(date);
        if (date[0]>this._months[date[1]-1].NumberOfDays){
            date[0] = date[0] - this._months[date[1]-1].NumberOfDays;
            date[1] += 1;
            date = this.FixMonth(date);
            return this.FixDate(date);
        }
        return date;
    }

    get ControlsChangeCurDate(){
        if (this._controlsChangeDateWrapper !== undefined){
            return this._controlsChangeDateWrapper;
        }
        var wrapper = document.createElement('div');
        wrapper.classList.add('row');
        var leftpart = document.createElement('div');
        leftpart.classList.add('column', 'centered-element');
        var prevday = document.createElement('a');
        prevday.classList.add('button', 'round');
        prevday.innerText = 'Change to previous day';
        prevday.onclick = function(){
            var date = document.calData.FixDate([parseInt(document.calData.ChangeCurDateForm.day.value) - 1, 
                parseInt(document.calData.ChangeCurDateForm.month.value),
                parseInt(document.calData.ChangeCurDateForm.year.value)]);
            document.calData.UpdateCurrentDate(date[0], date[1], date[2]);
        }
        leftpart.appendChild(prevday);
        wrapper.appendChild(leftpart);

        var middlepart = document.createElement('div');
        middlepart.classList.add('column', 'centered-element');
        middlepart.appendChild(this.ChangeCurDateForm);
        wrapper.appendChild(middlepart);

        var rightpart = document.createElement('div');
        rightpart.classList.add('column', 'centered-element');
        var nextday = document.createElement('a');
        nextday.innerText = 'Change to next day';
        nextday.classList.add('button', 'round');
        nextday.onclick = function(){
            var date = document.calData.FixDate([parseInt(document.calData.ChangeCurDateForm.day.value) + 1, 
                parseInt(document.calData.ChangeCurDateForm.month.value),
                parseInt(document.calData.ChangeCurDateForm.year.value)]);
            document.calData.UpdateCurrentDate(date[0], date[1], date[2]);
        }
        rightpart.appendChild(nextday);
        wrapper.appendChild(rightpart);


        this._controlsChangeDateWrapper = wrapper;
        return wrapper;
    }

    fillContainers(){
        if (this._containerCalendar !== undefined){
            this.MonthTables;
        }
        if (this._containerControls !== undefined){
            this._containerControls.appendChild(this.ControlsCurDate);
        }
        if (this._curDateSetup !== undefined){
            if (this.Editable){
                this._curDateSetup.appendChild(this.ControlsChangeCurDate);
            }
        }
        if (this.Redirect){
            if (this._redirectTarget !== undefined){
                this._redirectTarget.scrollIntoView();
                this._redirectTarget = undefined;
                this._redirect = false;
            }
        }
    }
}

class CalendarMonth{    
    constructor(id=undefined, name=undefined, number=undefined, numberofdays=undefined){
        this._id = id;
        this._name = name;
        this._number = number;
        this._numberofdays = numberofdays;
    }

    static fromDictionary(dict, link=undefined){
        return new CalendarMonth(dict['id'], dict['monthname'], dict['monthnumber'], dict['numberofdays']);
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._name = dict['monthname'];
        this._number = dict['monthnumber'];
        this._numberofdays = dict['numberofdays'];
    }

    get ID(){
        return this._id;
    }

    get Name(){
        return this._name;
    }

    get MonthNumber(){
        if (this._number == undefined)
            return 1;
        return this._number;
    }

    get NumberOfDays(){
        if (this._numberofdays == undefined)
            return 1;
        return this._numberofdays;
    }
}

class CalendarWeekDay{
    
    constructor(id=undefined, name=undefined, number=undefined, workday=true){
        this._id = id;
        this._name = name;
        this._daynumber = number;
        this._workday = workday;
    }

    static fromDictionary(dict, link=undefined){
        return new CalendarWeekDay(dict['id'], dict['dayname'], dict['daynumber'], dict['workday']);
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._name = dict['dayname'];
        this._daynumber = dict['daynumber'];
        this._workday = dict['workday'];
    }

    get ID(){
        return this._id;
    }

    get Name(){
        return this._name;
    }

    get DayNumber(){
        if (this._daynumber == undefined)
            return 1;
        return this._daynumber;
    }

    get Workday(){
        if (this._workday == undefined)
            return true;
        return this._workday;
    }

    get submitLink(){
        if (this._submitlink === undefined){
            return window.location.pathname+'/weekday';
        }
        return this._submitlink;
    }
}