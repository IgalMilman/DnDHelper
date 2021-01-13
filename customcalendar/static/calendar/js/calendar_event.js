class CalendarEvent{
    static object = undefined;

    constructor(id=undefined, apilink=undefined, directlink=undefined, day=0, month=0, year=0, calendardata=undefined){
        this._id = id;
        this._apilink = apilink;
        this._directlink = directlink;
        this._permlink = undefined;
        this._title = undefined;
        this._month = month;
        this._day = day;
        this._year = year;
        this._text = undefined;
        this._calendarData = calendardata;
        this._editable = false;
    }

    get ID(){
        return this._id;
    }

    get Day(){
        if (this._day === undefined){
            return 0;
        }
        return this._day;
    }

    get Month(){
        if (this._month === undefined){
            return 0;
        }
        return this._month;
    }

    get Year(){
        if (this._year === undefined){
            return 0;
        }
        return this._year;
    }

    get Text(){
        if (this._text === undefined){
            this.updateFromAjax();
        }
        return this._text;
    }

    get Title(){
        if (this._title === undefined){
            return '';
        }
        return this._title;
    }

    get CalendarData(){
        if (this._calendarData === undefined){
            return document.calData;
        }
        return this._calendarData;
    }

    get APILink(){
        if (this._apilink === undefined){
            return window.location.pathname + '/a/event/'+this.ID;
        }
        return this._apilink;
    }

    get DirectLink(){
        if (this._directlink === undefined){
            return window.location.pathname + '/event/'+this.ID;
        }
        return this._directlink;
    }

    get DirectLinkPermission(){
        if (this._permlink === undefined){
            return this.DirectLink+'/perm';
        }
        return this._permlink;
    }

    get ChangeLink(){
        if (this._changelink === undefined){
            if (window.location.pathname.endsWith('/')){
                return window.location.pathname + 'event/edit';
            }
            return window.location.pathname + '/event/edit';
        }
        return this_changelink;
    }

    get Editable(){
        if (this._editable === undefined){
            return false;
        }
        return this._editable;
    }

    static fromDictionary(dict){
        var result = new CalendarEvent();
        result.updateDataDictionary(dict);
        return result;
    }

    updateDataDictionary(dict){
        this._id = dict['unid'];
        this._apilink = dict['apilink'];
        this._directlink = dict['directlink'];
        this._year = dict['year'];
        this._month = dict['month'];
        this._day = dict['day'];
        this._title = dict['title'];
        this._text = dict['text'];
        this._editable = dict['editable'];
    }

    updateFromAjax(requestLink = undefined){
        if (requestLink === undefined)
            requestLink = this.APILink;
        sendGetAjax(requestLink, undefined, 
            function(data, status){
                this.updateDataDictionary(data['event']);
            }, function(data, status){
                console.log(data);
            },
            false, this
        )
    }

    get EventLinkElement(){
        if (this._linkElement !== undefined){
            return this._linkElement;
        }
        var result = document.createElement('p');
        //result.classList.add('nomargin');
        var link = document.createElement('a');
        link.data = this;
        link.onclick = function(){
            this.data.OpenPopup();
            return false;
        };
        link.innerText = this.Title;
        result.appendChild(link);
        this._linkElement = result;
        return result;
    }

    get ChangeCalendarEventForm(){
        var form = document.createElement('form');
        form.classList.add('inlineblock');
        form.method = "POST";
        form.action = this.ChangeLink;
        form.enctype = "multipart/form-data";
        var input = document.createElement('input');
        input.type='hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = my_crsf_token;
        form.appendChild(input);
        var input = document.createElement('input');
        input.type='hidden';
        input.name = 'action';
        input.value = "change";
        form.appendChild(input);
        var input = document.createElement('input');
        input.type='hidden';
        input.name = 'targetid';
        input.value = this.ID;
        form.appendChild(input);
        var input = document.createElement('a');
        input.classList.add('button', 'round', 'inlineblock');
        input.onclick = function(){
            this.parentElement.submit();
        }
        input.innerText = 'Edit event';
        form.appendChild(input);
        return form;
    }

    get EventPopup(){
        if (this._popup !== undefined){
            return this._popup;
        }
        var result = document.createElement('div');
        this._popup = result;
        result.classList.add('reveal');
        result.classList.add('large');
        result.id = generateElementID('popup-');

        var closebutton = document.createElement('a');
        closebutton.classList.add('close-button');
        closebutton.setAttribute('data-close','');
        closebutton.setAttribute('aria-label','Close modal');
        closebutton.setAttribute('type','button');
        var internalclose = document.createElement('span');
        internalclose.setAttribute('aria-hidden', 'true');
        internalclose.innerHTML = '&times;';
        closebutton.appendChild(internalclose);
        result.appendChild(closebutton);
        document.body.appendChild(result);

        var month = this.CalendarData.getMonth(this.Month);
        var title = document.createElement('h4');
        title.innerText = this.Title;
        result.appendChild(title);
        var dateplace = document.createElement('p');
        if (month !== undefined){
            dateplace.innerText = this.Day.toString() + ' ' + month.Name + ' ' + this.Year; 
        }
        else{
            dateplace.innerText = this.Day.toString() + '/' + this.Month + '/' + this.Year; 
        }
        result.appendChild(dateplace);
        var textplace = document.createElement('div');
        textplace.classList.add('ql', 'ql-div');
        textplace.innerHTML = this.Text;
        result.appendChild(textplace);
        if (this.Editable){
            result.appendChild(this.ChangeCalendarEventForm);
            var changepermissions = document.createElement('a');
            changepermissions.classList.add('button', 'round', 'inlineblock');
            changepermissions.innerText = 'Change permissions';
            changepermissions.data = this;
            changepermissions.onclick = function(){
                var p = new PermissionPopup(this.data.DirectLinkPermission);
                p.Activate();
            }
            result.appendChild(changepermissions);
        }
        var openpagelink = document.createElement('a');
        openpagelink.classList.add('button', 'round', 'inlineblock');
        openpagelink.href = this.DirectLink;
        openpagelink.innerText = 'Event page';
        result.appendChild(openpagelink);
        var tmp = document.createElement('a');
        tmp.classList.add('invisible');
        result.appendChild(tmp);
        return result;
    }

    OpenPopup(){
        if (this._foundationPopup !== undefined){
            this._foundationPopup.open();
            return;
        }
        this._foundationPopup = new Foundation.Reveal($('#'+this.EventPopup.id));
        this._foundationPopup.open();
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