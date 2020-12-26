class CalendarData{
    static object = undefined;

    constructor(id=undefined, link=undefined, containerControls=undefined, containerCalendar=undefined){
        this._id = id;
        this._submitlink = link;
        this._containerControls = containerControls;
        this._containerCalendar = containerCalendar;
        this._months = [];
        this._weekdays = [];
        this._yearTables = {};
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
            return window.location.href+'/general';
        }
        return this._submitlink;
    }

    setCurrentDate(day, month, year){
        this._currentDate = [day, month, year];
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
        return new CalendarData(dict['id'], dict['firstyear'], link);
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
        this.updateDataDictionaryMonths(dict['months']);
        this.updateDataDictionaryWeekDays(dict['week']['days']);
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
            }
        )
    }

    createViewForOneMonth(date, firstday){
        var wrapper = document.createElement('div');
        wrapper.classList.add('calendar-wrapper');
        var header = document.createElement('h4');
        var montha = document.createElement('a');
        montha.id= date[2].toString() + '-' + date[1].toString();
        montha.href= '#' + date[2].toString() + '-' + date[1].toString();
        montha.innerText = this._months[date[1]-1].Name+' '+date[2].toString();
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
            var daya = document.createElement('a');
            daya.id= date[2].toString() + '-' + date[1].toString() + '-' + (i+1).toString();
            day.innerText = (i+1).toString();
            day.appendChild(daya);
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

    get Controls(){
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
        this._containerControls.appendChild(wrapper);
        return wrapper;
    }

    fillContainers(){
        if (this._containerCalendar !== undefined){
            this.MonthTables;
        }
        if (this._containerControls !== undefined){
            this.Controls;
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
            return window.location.href+'/weekday';
        }
        return this._submitlink;
    }
}