function sendPostAjax(link, data, success, failure, async = true) {
    data['csrfmiddlewaretoken'] = my_crsf_token;
    $.ajax({
        type: "POST",
        url: link,
        data: data,
        success: success,
        failure: failure,
        async: async
    })
}

function dictToURI(dict) {
    var str = [];
    for(var p in dict){
        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(dict[p]));
    }
    return str.join("&");
}

function sendGetAjax(link, data, success, failure, async = true) {
    var fulllink = (' ' + link).slice(1);
    if(data !== undefined){
        if (!fulllink.includes('?')){
            fulllink = fulllink + '?'+dictToURI(data);
        }
        else{
            if(!fulllink.endsWith('&'))
                fulllink+='&';
            fulllink+=dictToURI(data);            
        }
    }
    $.ajax({
        type: "GET",
        url: fulllink,
        success: success,
        failure: failure,
        async: async
    })
}