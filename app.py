from  flask import Flask, render_template,request,jsonify
app = Flask(__name__)

@app.route('/myapp/find_danger')
def api_all():
    #if request.args['lats'] and request.args['lons'] and request.args['lats'].isnumeric() and request.args['lons'].isnumeric() and abs(request.args['lats'])<90 and abs(request.args['lons'])<180:
    if 'lats' and 'lons' in request.args :

        #return request.args['id2']
        import numpy as np
        import pandas as pd
        from sklearn.cluster import DBSCAN
        from geopy.distance import great_circle
        from shapely.geometry import MultiPoint
    #import json

        df = pd.read_json("mydata_time.json")
    #print(df)
        df=df.loc[(df['time'] >= 6) & (df['time'] <= 18)]
    #print(df)
        coords = df.as_matrix(columns=['lati', 'long'])
        kms_per_radian = 6371.0088
        epsilon = 1/ kms_per_radian
        db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
        if clusters[clusters.size-1].size==0:
            clusters=clusters[:clusters.size-1]
        #print('Number of clusters: {}'.format(clusters.size))

        dist_max=[]

        def get_centermost_point(cluster):
            centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
            max_dist_point = max(cluster, key=lambda point: great_circle(point, centroid).m)
            coords_1 = (max_dist_point[0], max_dist_point[1])
            coords_2 = (centroid[0], centroid[1])
            dist_max.append(great_circle(coords_1, coords_2).km)
            return centroid

        res = clusters.map(get_centermost_point)
        final=[]
        def create_json(res,dist):
            for x in range(len(dist)):
                s={}
                s["lat"]=res[x][0]
                s["lon"]=res[x][1]
                s["radius"]=dist[x]
            #print(s)
                final.append(s)
        create_json(res,dist_max)

        res=False
        for k in range(len(final)):
            coords_1 = (final[k]['lat'], final[k]['lon'])
            coords_2 = (request.args['lats'],request.args['lons'])
            dist=great_circle(coords_1, coords_2).km
            if(dist<=final[k]['radius']):
                res=True
                break


        #print(final)
        return jsonify({"result":res})
    else:
        return jsonify({"result":'Error'})

if __name__== '__main__':
    app.run()


