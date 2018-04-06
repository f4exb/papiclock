#!/usr/bin/env python
import web, json

meteo_dict = {
    "update_ts" : 0,
    "run_number": 0,
    "geoloc" : {
        "lat": 0,
        "lon": 0
    },
    "data": {}
}

urls = (
    '/meteo', 'web_process_meteo'
)

class MyApp(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

app = MyApp(urls, globals())

class web_process_meteo:
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        output = json.dumps(meteo_dict)
        return output

def run(port = 8080):
    app.run(port=port)

def stop():
    app.stop()
