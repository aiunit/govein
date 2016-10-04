Vue.use(VueResource);

Vue.http.interceptors.push(function (request, next) {
    // 这里对请求体进行处理
    request.headers = request.headers || {};
    var params = /csrftoken=(.+);/.exec(document.cookie);
    if (params && params[1]) {
        request.headers.append('X-CSRFToken', params[1]);
    }
    next();
});