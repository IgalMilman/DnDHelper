class User{
    constructor(username=undefined, fullname=undefined, issuper=false){
        this.username=username;
        this.fullname=fullname;
        this.issuper=issuper;
        this.permissions = {};
    }

    static fromDictionary(dict){
        return new User(dict['username'], dict['fullname'], dict['issuper']);
    }

    static createTables(sections){
        var table = document.createElement('table');
        var tid = generateElementID('table-');
        table.id = tid;
        var thead = document.createElement('thead');
        table.appendChild(thead);
        var headerrow = document.createElement('tr');
        thead.appendChild(headerrow);
        var headercell = document.createElement('th');
        headercell.innerText = 'Username';
        headerrow.appendChild(headercell);
        headercell = document.createElement('th');
        headercell.innerText = 'Full name';
        headerrow.appendChild(headercell);
        for (const section in sections) {
            headercell = document.createElement('th');
            headercell.innerText = sections[section].sectiontitle;
            headerrow.appendChild(headercell);
        }
        var tbody = document.createElement('tbody');
        table.appendChild(tbody);
        table.tbody = tbody;
        return table;
    }

    createRow(sections){
        var row = document.createElement('tr');
        var cell = document.createElement('td');
        cell.innerText = this.username;
        row.appendChild(cell);
        cell = document.createElement('td');
        cell.innerText = this.fullname;
        row.appendChild(cell);
        for (const section in sections) {
            var perm = this.getPermission( sections[section].sectionid);
            cell = document.createElement('td');
            cell.appendChild(perm.createSelectElement());
            var button = document.createElement('a');
            button.classList.add('button', 'round', 'inlineblock', 'distanceleft');
            button.innerText = 'Save';
            button.permission= perm;
            perm.set_button(button);
            button.onclick = function(){this.permission.sendinfo();return false;}
            cell.appendChild(button);
            row.appendChild(cell);
        }
        return row;
    }

    addPermission(sectionid, permission){
        this.permissions[sectionid] = permission;
    }

    getPermission(sectionid){
        if (sectionid in this.permissions){
            return this.permissions[sectionid];
        }
        return undefined;
    }
}

class Section{
    constructor(sectionid, sectiontitle, ispage = false){
        this.sectionid = sectionid;
        this.sectiontitle = sectiontitle;
        this.ispage = ispage;
    }

    static fromDictionary(dict){
        return new Section(dict['secid'], dict['sectitle']);
    }
}

class Permission{
    static PERMISSION_LEVELS=[];

    static object = undefined;

    static parsePermissionData(data, link){
        Permission.PERMISSION_LEVELS = data['permlevels'];
        var rawsections = data['sections'];
        var pagedata = data['page'];
        var users = {};
        var sections = {};
        if (pagedata !== undefined){
            var section = new Section(undefined, "Page", true);
            for (const secperm of pagedata) {
                var user = undefined;
                if(secperm['grantedto']['username'] in users){
                    user = users[secperm['grantedto']['username']];
                }
                else{
                    user = User.fromDictionary(secperm['grantedto']);
                    users[user.username] = user;
                }
                var perm = new Permission(section.sectionid, user.username, secperm['permlevel'], link, true);
                user.addPermission(section.sectionid, perm);
            }
            sections[section.sectionid] = section;
        }
        for (const rawsection of rawsections) {
            var section = Section.fromDictionary(rawsection);
            for (const secperm of rawsection['secperm']) {
                var user = undefined;
                if(secperm['grantedto']['username'] in users){
                    user = users[secperm['grantedto']['username']];
                }
                else{
                    user = User.fromDictionary(secperm['grantedto']);
                    users[user.username] = user;
                }
                var perm = new Permission(section.sectionid, user.username, secperm['permlevel'], link);
                user.addPermission(section.sectionid, perm);
            }
            sections[section.sectionid] = section;
        }
        return {'users': users, 'sections': sections};
    }

    constructor(unid=undefined, username=undefined, plevel=0, link='', ispage=false){
        this.permlevel = plevel;
        this.username = username;
        this.unid = unid;
        this.link = link;
        this.ispage = ispage;
    }

    getUsername(){
        if (this.username !== undefined && this.username!==null){
            return this.username;
        }
        return 'all';
    }

    getUnid(){
        if (this.unid !== undefined && this.unid!==null){
            return this.unid;
        }
        return 'all';
    }

    createSelectElement(){
        this.selectElement = document.createElement("select");
        this.selectElement.id = "select-"+this.getUsername()+"-"+this.getUnid();
        this.selectElement.classList.add('inlineblock', 'larger_part');
        this.selectElement.name = this.selectElement.id;

        for (const plevel of Permission.PERMISSION_LEVELS) {
            var optionElement = document.createElement("option");
            optionElement.id = this.selectElement.id + "-"+plevel[1];
            optionElement.value = plevel[0];
            optionElement.innerText = plevel[1];
            this.selectElement.appendChild(optionElement);
            if (this.permlevel == plevel[0]){
                this.selectElement.value = plevel[0];
            }            
        }
        return this.selectElement;
    }

    createData(){
        if (this.ispage){
            return {'username':this.getUsername(), 'permissionlevel': this.selectElement.value, 'action':'setperm'};
        }
        return {'username':this.getUsername(), 'permissionlevel': this.selectElement.value, 'targetid': this.getUnid(), 'action':'setperm'};
    }

    successfullySentInfo(data, status){
        console.log(data);
        console.log(status);
        Permission.object.button.classList.remove('alert');
        Permission.object.button.classList.add('success');
    }

    failledSentInfo(data, status){
        Permission.object.button.classList.add('alert');
        Permission.object.button.classList.remove('success');
    }

    set_button(button){
        this.button = button;
    }

    sendinfo(){
        this.button.classList.remove('success');
        this.button.classList.remove('alert');
        Permission.object = this;
        sendPostAjax(this.link, this.createData(), this.successfullySentInfo, this.failledSentInfo, false);
    }
}

class PermissionPopup{
    static obj;

    constructor(url, unid=undefined){
        this.url = url;
        this.originialUrl = url;
        if (unid === undefined)
            this.unid = 'all';
        else 
            this.unid = unid;
    }

    AjaxCallback(data, status){
        if (status == 'success'){
            this.SuccessAjaxGet(data, status);
        }
    }

    SuccessAjaxGet(data, status){
        this.popup = document.createElement('div');
        this.popup.classList.add('reveal');
        this.popup.classList.add('large');
        this.popup.id = generateElementID('popup-');
        this.data=Permission.parsePermissionData(data, this.url);
        this.sections = this.data['sections'];
        this.users = this.data['users'];
        this.table=User.createTables(this.sections);
        for (const u in this.users) {
            this.table.tbody.appendChild(this.users[u].createRow(this.sections));
        }
        this.popup.appendChild(this.table);
        var closebutton = document.createElement('a');
        closebutton.classList.add('close-button');
        closebutton.setAttribute('data-close','');
        closebutton.setAttribute('aria-label','Close modal');
        closebutton.setAttribute('type','button');
        var internalclose = document.createElement('span');
        internalclose.setAttribute('aria-hidden', 'true');
        internalclose.innerHTML = '&times;';
        closebutton.appendChild(internalclose);
        this.popup.appendChild(closebutton);
        document.body.appendChild(this.popup);
        this.dataTableTable = $('#'+this.table.id).DataTable({
            "lengthMenu": [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
            "iDisplayLength": -1
        });
        var confirmation = new Foundation.Reveal($('#'+this.popup.id));
        confirmation.open();
    }

    FailedAjaxGet(data, status){
        
    }

    Activate(){
        PermissionPopup.obj=this;
        sendGetAjax(this.url, {'target': this.unid}, function(data, status){PermissionPopup.obj.AjaxCallback(data, status)});

    }
}