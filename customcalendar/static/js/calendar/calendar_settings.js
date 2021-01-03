class CalendarData{
    static object = undefined;

    constructor(id=undefined, firstyear=undefined, link=undefined, containerGeneral=undefined, containerMonths=undefined, containerWeeks=undefined){
        this._id = id;
        this._firstyear = firstyear;
        this._submitlink = link;
        this._containerGeneral = containerGeneral;
        this._containerMonths = containerMonths;
        this._containerWeeks = containerWeeks;
        this._months = [];
        this._weekdays = [];
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

    get submitLink(){
        if (this._submitlink === undefined){
            return window.location.href+'/general';
        }
        return this._submitlink;
    }
    static fromDictionary(dict, link=undefined){
        return new CalendarData(dict['id'], dict['firstyear'], link);
    }

    updateData(){
        this._firstyear = this.Form.firstyear.value;
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
        this.updateMonthsData();
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._firstyear = dict['firstyear'];
        this.updateDataDictionaryMonths(dict['months']);
        this.updateDataDictionaryWeekDays(dict['week']['days']);
    }

    get jsonData(){
        result = {
            'targetid': this.ID, 
            'firstyear': this.firstYear, 
            'action':'changed'
        };
        return result;
    }

    get monthMessagePlace(){
        if (this._monthsMessagePlace !== undefined){
            return this._monthsMessagePlace;
        }
        if (this._containerMonths === undefined)
            return undefined;
        this._monthsMessagePlace = document.createElement('p');
        this._monthsMessagePlace.classList.add('hidden');
        if (this._monthsTable!==undefined){
            this._containerMonths.insertBefore(this._monthsMessagePlace, this._monthsTable);
        }
        else{
            this._containerMonths.appendChild(this._monthsMessagePlace);
        }
        return this._monthsMessagePlace;
    }

    updateMonthsData(){
        if (this._containerMonths!==undefined){
            if (this._monthsTable===undefined){
                this._monthsTable = document.createElement('table');
                this._monthsTable.classList.add('inputTable');
                this._monthsTable.appendChild(CalendarMonth.createMonthsHeaderRow());
            }
            var table = this._monthsTable;
            this._months.sort(function(a,b){
                return a.MonthNumber - b.MonthNumber;
            });
            while (table.childElementCount > 1) {
                table.removeChild(table.lastChild);
            }
            for(var i = 0; i<this._months.length; i++){
                table.appendChild(this._months[i].Row);
            }
            table.appendChild(CalendarMonth.createNewElementForm(this._months.length+1));
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
        this.updateWeekDaysData();
    }

    get weekDayMessagePlace(){
        if (this._weekdaysMessagePlace !== undefined){
            return this._weekdaysMessagePlace;
        }
        if (this._containerWeeks === undefined)
            return undefined;
        this._weekdaysMessagePlace = document.createElement('p');
        this._weekdaysMessagePlace.classList.add('hidden');
        if (this._weekdaysTable!==undefined){
            this._containerWeeks.insertBefore(this._weekdaysMessagePlace, this._weekdaysTable);
        }
        else{
            this._containerWeeks.appendChild(this._weekdaysMessagePlace);
        }
        return this._weekdaysMessagePlace;
    }

    updateWeekDaysData(){
        if (this._containerWeeks!==undefined){
            if (this._weekdaysTable===undefined){
                this._weekdaysTable = document.createElement('table');
                this._weekdaysTable.classList.add('inputTable');
                this._weekdaysTable.appendChild(CalendarWeekDay.createWeekDayHeaderRow());
            }
            var table = this._weekdaysTable;
            this._weekdays.sort(function(a,b){
                return a.MonthNumber - b.MonthNumber;
            });
            while (table.childElementCount > 1) {
                table.removeChild(table.lastChild);
            }
            for(var i = 0; i<this._weekdays.length; i++){
                table.appendChild(this._weekdays[i].Row);
            }
            table.appendChild(CalendarWeekDay.createNewElementForm(this._weekdays.length+1));
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

    submitData(){
        sendPostAjax(this.submitLink, this.jsonData, 
            function(data, status){
                document.calData.messageplace.classList.add('success');
                document.calData.messageplace.classList.remove('error');
                document.calData.messageplace.innerText=data['message'];
                document.calData.messageplace.classList.remove('hidden');
            }, 
            function(data, status){
                document.calData.messageplace.classList.add('error');
                document.calData.messageplace.classList.remove('success');
                document.calData.messageplace.innerText=data['message'];
                document.calData.messageplace.classList.remove('hidden');
            });
    }

    get Form(){
        if (this._form!==undefined){
            return this._form;
        }
        var form = document.createElement('form');
        form.id = generateElementID('calendar-form-');
        var messageplace = document.createElement('p');
        this._form=form;
        messageplace.classList.add('hidden');
        this.messageplace = messageplace;
        form.appendChild(messageplace);
        var idinput = document.createElement('input');
        idinput.type = 'hidden';
        idinput.name = 'targetid';
        idinput.value = this.ID;
        form.appendChild(idinput);
        var yearinput = document.createElement('input');
        yearinput.type = 'number';
        yearinput.name = 'firstyear';
        yearinput.value = this.firstYear;
        yearinput.required = true;
        form.yearinput = yearinput;
        var sur = document.createElement('p');
        sur.appendChild(yearinput);
        form.appendChild(sur);
        form.data = this;
        var submitbutton = document.createElement('button');
        submitbutton.type="submit";
        submitbutton.classList.add('button', 'save', 'round');
        submitbutton.innerText = 'Save changes';
        submitbutton.data = this;
        submitbutton.curform = form;
        submitbutton.onclick = function(){
            this.data.updateData();
            this.data.submitData();
            return false;
        }
        form.appendChild(submitbutton);
        return form;
    }

    fillContainers(){
        if (this._containerGeneral !== undefined){
            this._containerGeneral.appendChild(this.Form);
        }
        if (this._containerMonths !== undefined){
            if (this._monthsTable !== undefined){
                this._containerMonths.appendChild(this._monthsTable);
            }
        }
        if (this._containerWeeks !== undefined){
            if (this._weekdaysTable !== undefined){
                this._containerWeeks.appendChild(this._weekdaysTable);
            }
        }
    }

    createHiddenInput(){
        var input = document.createElement('input');
        input.type='hidden';
        input.name = 'calid';
        input.value = this.ID;
        return input;
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

    static createMonthsHeaderRow(){
        var row = document.createElement('tr');
        var cell = document.createElement('th');
        cell.innerText = 'Month name';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Month number';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Number of days';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Action';
        row.appendChild(cell);
        return row;
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._name = dict['monthname'];
        this._number = dict['monthnumber'];
        this._numberofdays = dict['numberofdays'];
    }

    static createNewElementForm(currentMonths=1){
        var obj = new CalendarMonth(undefined, '', currentMonths, 1);
        return obj.Row;
    }

    get jsonData(){
        var result = {
            'calid': document.calData.ID,
            'monthname': this.Name, 
            'monthnumber': this.MonthNumber, 
            'numberofdays': this.NumberOfDays, 
        };
        if (this.ID === undefined){
            result['action'] = 'add';
        }
        else{
            result['targetid'] = this.ID; 
            result['action'] = 'changed';
        }
        return result;
    }

    updateData(){
        this._name = this._tableRowNameInput.value;
        this._number = this._tableRowMNInput.value;
        this._numberofdays = this._tableRowDNInput.value;
    }

    submitData(){
        sendPostAjax(this.submitLink, this.jsonData, 
            function(data, status){
                document.calData.monthMessagePlace.classList.add('success');
                document.calData.monthMessagePlace.classList.remove('error');
                document.calData.monthMessagePlace.innerText=data['message'];
                document.calData.monthMessagePlace.classList.remove('hidden');
                document.calData.updateFromAjax();
            }, 
            function(data, status){
                document.calData.monthMessagePlace.classList.add('error');
                document.calData.monthMessagePlace.classList.remove('success');
                document.calData.monthMessagePlace.innerText=data['message'];
                document.calData.monthMessagePlace.classList.remove('hidden');
            });
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

    get submitLink(){
        if (this._submitlink === undefined){
            return window.location.href+'/months';
        }
        return this._submitlink;
    }

    get Row(){
        if (this._tableRow !== undefined){
            return this._tableRow;
        }
        var row = document.createElement('tr');
        this._tableRow = row;
        var cell = document.createElement('td');
        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'name';
        input.value = this.Name;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowNameInput = input;
        var cell = document.createElement('td');
        var input = document.createElement('input');
        input.type = 'number';
        input.name = 'number';
        input.value = this.MonthNumber;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowMNInput = input;
        var cell = document.createElement('td');
        var input = document.createElement('input');
        input.type = 'number';
        input.name = 'numberdays';
        input.value = this.NumberOfDays;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowDNInput = input;
        var cell = document.createElement('td');
        cell.classList.add('centered-element');
        var submitbutton = document.createElement('button');
        submitbutton.type = 'submit';
        submitbutton.value = this.Name;
        submitbutton.classList.add('button', 'save', 'round', 'center');
        submitbutton.innerText = 'Save changes';
        submitbutton.data = this;
        submitbutton.onclick = function(){
            this.data.updateData();
            this.data.submitData();
            return false;
        }

        cell.appendChild(submitbutton);
        row.appendChild(cell);
        this._tableRowSubmit = submitbutton;
        return row;
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

    static createWeekDayHeaderRow(){
        var row = document.createElement('tr');
        var cell = document.createElement('th');
        cell.innerText = 'Week day name';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Week day number';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Is workday?';
        row.appendChild(cell);
        var cell = document.createElement('th');
        cell.innerText = 'Action';
        row.appendChild(cell);
        return row;
    }

    updateDataDictionary(dict){
        this._id = dict['id'];
        this._name = dict['dayname'];
        this._daynumber = dict['daynumber'];
        this._workday = dict['workday'];
    }

    static createNewElementForm(currentDays=1){
        var obj = new CalendarWeekDay(undefined, '', currentDays, true);
        return obj.Row;
    }

    get jsonData(){
        var result = {
            'calid': document.calData.ID,
            'dayname': this.Name, 
            'daynumber': this.DayNumber, 
            'workday': this.Workday ? "True" : "False", 
        };
        if (this.ID === undefined){
            result['action'] = 'add';
        }
        else{
            result['targetid'] = this.ID; 
            result['action'] = 'changed';
        }
        return result;
    }

    updateData(){
        this._name = this._tableRowNameInput.value;
        this._daynumber = this._tableRowDNInput.value;
        this._workday = this._tableRowWorkdayInput.checked;
    }

    submitData(){
        sendPostAjax(this.submitLink, this.jsonData, 
            function(data, status){
                document.calData.weekDayMessagePlace.classList.add('success');
                document.calData.weekDayMessagePlace.classList.remove('error');
                document.calData.weekDayMessagePlace.innerText=data['message'];
                document.calData.weekDayMessagePlace.classList.remove('hidden');
                document.calData.updateFromAjax();
            }, 
            function(data, status){
                document.calData.weekDayMessagePlace.classList.add('error');
                document.calData.weekDayMessagePlace.classList.remove('success');
                document.calData.weekDayMessagePlace.innerText=data['message'];
                document.calData.weekDayMessagePlace.classList.remove('hidden');
            });
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

    get Row(){
        if (this._tableRow !== undefined){
            return this._tableRow;
        }
        var row = document.createElement('tr');
        this._tableRow = row;
        var cell = document.createElement('td');
        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'name';
        input.value = this.Name;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowNameInput = input;
        var cell = document.createElement('td');
        var input = document.createElement('input');
        input.type = 'number';
        input.name = 'number';
        input.value = this.DayNumber;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowDNInput = input;
        var cell = document.createElement('td');
        cell.classList.add('centered-element');
        var input = document.createElement('input');
        input.type = 'checkbox';
        input.name = 'numberdays';
        input.checked = this.Workday;
        input.value = this.Workday;
        cell.appendChild(input);
        row.appendChild(cell);
        this._tableRowWorkdayInput = input;
        var cell = document.createElement('td');
        cell.classList.add('centered-element');
        var submitbutton = document.createElement('button');
        submitbutton.type = 'submit';
        submitbutton.value = this.Name;
        submitbutton.classList.add('button', 'save', 'round', 'center');
        submitbutton.innerText = 'Save changes';
        submitbutton.data = this;
        submitbutton.onclick = function(){
            this.data.updateData();
            this.data.submitData();
            return false;
        }
        cell.appendChild(submitbutton);
        row.appendChild(cell);
        this._tableRowSubmit = submitbutton;
        return row;
    }
}