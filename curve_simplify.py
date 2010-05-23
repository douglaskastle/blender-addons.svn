# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
'''
This script simplifies Curves.
'''
bl_addon_info = {
    'name': 'Curve: simplify curves',
    'author': 'testscreenings',
    'version': '1',
    'blender': (2, 5, 2),
    'location': '3dviev > simplify curves',
    'url': '',
    'description': 'this script simplifies curves',
    'category': 'Object'}
####################################################
import bpy
from bpy.props import *
import mathutils
import math

##############################
#### simplipoly algorithm ####
##############################
# get SplineVertIndicies to keep
def simplypoly(splineVerts, options):
    # main vars
    newVerts = [] # list of vertindices to keep
    points = splineVerts # list of 3dVectors
    pointCurva = [] # table with curvatures
    curvatures = [] # averaged curvatures per vert
    for p in points:
        pointCurva.append([])
    order = options[3] # order of sliding beziercurves
    k_thresh = options[2] # curvature threshold
    dis_error = options[6] # additional distance error

    # get curvatures per vert
    for i, point in enumerate(points[:-(order-1)]):
        BVerts = points[i:i+order]
        for b, BVert in enumerate(BVerts[1:-1]):
            deriv1 = getDerivative(BVerts, 1/(order-1), order-1)
            deriv2 = getDerivative(BVerts, 1/(order-1), order-2)
            curva = getCurvature(deriv1, deriv2)
            pointCurva[i+b+1].append(curva)

    # average the curvatures
    for i in range(len(points)):
        avgCurva = sum(pointCurva[i]) / (order-1)
        curvatures.append(avgCurva)

    # get distancevalues per vert - same as Ramer-Douglas-Peucker
    # but for every vert
    distances = [0.0] #first vert is always kept
    for i, point in enumerate(points[1:-1]):
        dist = altitude(points[i], points[i+2], points[i+1])
        distances.append(dist)
    distances.append(0.0) # last vert is always kept

    # generate list of vertindicies to keep
    # tested against averaged curvatures and distances of neighbour verts
    newVerts.append(0) # first vert is always kept
    for i, curv in enumerate(curvatures):
        if (curv > k_thresh*0.1
        or distances[i] > dis_error*0.1):
            newVerts.append(i)
    newVerts.append(len(curvatures)-1) # last vert is always kept

    return newVerts

# get binomial coefficient
def binom(n, m):
    b = [0] * (n+1)
    b[0] = 1
    for i in range(1, n+1):
        b[i] = 1
        j = i-1
        while j > 0:
            b[j] += b[j-1]
            j-= 1
    return b[m]

# get nth derivative of order(len(verts)) bezier curve
def getDerivative(verts, t, nth):
    order = len(verts) - 1 - nth
    QVerts = []
    for i in range(nth):
        if QVerts:
            verts = QVerts
        derivVerts = []
        for i in range(len(verts)-1):
            derivVerts.append(verts[i+1] - verts[i])
        QVerts = derivVerts
    point = mathutils.Vector((0, 0, 0))
    for i, vert in enumerate(QVerts):
        point += binom(order, i) * math.pow(t, i) * math.pow(1-t, order-i) * vert
    deriv = point
    return deriv

# get curvature from first, second derivative
def getCurvature(deriv1, deriv2):
    if deriv1.length == 0: # in case of points in straight line
        curvature = 0
        return curvature
    curvature = (deriv1.cross(deriv2)).length / math.pow(deriv1.length, 3)
    return curvature

#########################################
#### Ramer-Douglas-Peucker algorithm ####
#########################################
# get altitude of vert
def altitude(point1, point2, pointn):
    edge1 = point2 - point1
    edge2 = pointn - point1
    alpha = edge1.angle(edge2)
    altitude = math.sin(alpha) * edge2.length
    return altitude

# iterate through verts
def iterate(points, newVerts, error):
    new = []
    for newIndex in range(len(newVerts)-1):
        bigVert = 0
        alti_store = 0
        for i, point in enumerate(points[newVerts[newIndex]+1:newVerts[newIndex+1]]):
            alti = altitude(points[newVerts[newIndex]], points[newVerts[newIndex+1]], point)
            if alti > alti_store:
                alti_store = alti
                if alti_store > error:
                   bigVert = i+1+newVerts[newIndex]
        if bigVert:
            new.append(bigVert)
    if new == []:
        return False
    return new

#### get SplineVertIndicies to keep
def simplify_RDP(splineVerts, options):
    #main vars
    error = options[4]

    # set first and last vert
    newVerts = [0, len(splineVerts)-1]

    # iterate through the points
    new = 1
    while new != False:
        new = iterate(splineVerts, newVerts, error)
        if new:
            newVerts += new
            newVerts.sort()
    return newVerts

##########################
#### CURVE GENERATION ####
##########################
# set bezierhandles to auto
def setBezierHandles(newCurve):
        scene = bpy.context.scene
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='AUTOMATIC')
        bpy.ops.object.mode_set(mode='OBJECT', toggle=True)

# get array of new coords for new spline from vertindices
def vertsToPoints(newVerts, splineVerts, splineType):
    # main vars
    newPoints = []

    # array for BEZIER spline output
    if splineType == 'BEZIER':
        for v in newVerts:
            newPoints += splineVerts[v].to_tuple()

    # array for nonBEZIER output
    else:
        for v in newVerts:
            newPoints += (splineVerts[v].to_tuple())
            if splineType == 'NURBS':
                newPoints.append(1) #for nurbs w=1
            else: #for poly w=0
                newPoints.append(0)
    return newPoints

#########################
#### MAIN OPERATIONS ####
#########################

def main(context, obj, options):
    #print("\n_______START_______")
    # main vars
    mode = options[0]
    output = options[1]
    degreeOut = options[5]
    keepShort = options[7]
    bpy.ops.object.select_all(action='DESELECT')
    scene = context.scene
    splines = obj.data.splines.values()

    # create curvedatablock
    curve = bpy.data.curves.new("simple_"+obj.name, type = 'CURVE')

    # go through splines
    for spline_i, spline in enumerate(splines):
        # test if spline is a long enough
        if len(spline.points) >= 7 or keepShort:
            #check what type of spline to create
            if output == 'INPUT':
                splineType = spline.type
            else:
                splineType = output
            
            # get vec3 list to simplify
            if spline.type == 'BEZIER': # get bezierverts
                splineVerts = spline.bezier_points.values()
                splineVerts = [splineVert.co.copy()
                                for splineVert in spline.bezier_points.values()]

            else: # verts from all other types of curves
                splineVerts = [splineVert.co.copy().resize3D()
                                for splineVert in spline.points.values()]

            # simplify spline according to mode
            if mode == 'distance':
                newVerts = simplify_RDP(splineVerts, options)

            if mode == 'curvature':
                newVerts = simplypoly(splineVerts, options)

            # convert indicies into vectors3D
            newPoints = vertsToPoints(newVerts, splineVerts, splineType)

            # create new spline            
            newSpline = curve.splines.new(type = splineType)

            # put newPoints into spline according to type
            if splineType == 'BEZIER':
                newSpline.bezier_points.add(int(len(newPoints)*0.33))
                newSpline.bezier_points.foreach_set('co', newPoints)
            else:
                newSpline.points.add(int(len(newPoints)*0.25 - 1))
                newSpline.points.foreach_set('co', newPoints)

            # set degree of outputNurbsCurve
            if output == 'NURBS':
                newSpline.order_u = degreeOut

            # splineoptions
            newSpline.endpoint_u = spline.endpoint_u

    # create ne object and put into scene
    newCurve = bpy.data.objects.new("simple_"+obj.name, curve)
    scene.objects.link(newCurve)
    newCurve.selected = True
    scene.objects.active = newCurve
    newCurve.matrix = obj.matrix

    # set bezierhandles to auto
    setBezierHandles(newCurve)

    #print("________END________\n")
    return

####################
##### OPERATOR #####
####################
class CURVE_OT_simplify(bpy.types.Operator):
    ''''''
    bl_idname = "curve.simplify"
    bl_label = "simplifiy curves"
    bl_description = "simplify curves"
    bl_options = {'REGISTER', 'UNDO'}

    ## Properties
    opModes = [
            ('distance', 'distance', 'distance'),
            ('curvature', 'curvature', 'curvature')]
    mode = EnumProperty(name="Mode",
                                    description="choose algorithm to use",
                                    items=opModes)
    SplineTypes = [
                ('INPUT', 'Input', 'same type as input spline'),
                ('NURBS', 'Nurbs', 'NURBS'),
                ('BEZIER', 'Bezier', 'BEZIER'),
                ('POLY', 'Poly', 'POLY')]
    output = EnumProperty(name="Output splines",
                                    description="Type of splines to output",
                                    items=SplineTypes)
    k_thresh = FloatProperty(name="k",
                            min=0, soft_min=0,
                            default=0,
                            description="threshold")
    pointsNr = IntProperty(name="n",
                            min=5, soft_min=5,
                            max=9, soft_max=9,
                            default=5,
                            description="degree of curve to get averaged curvatures")
    error = FloatProperty(name="error in Bu",
                                        description="maximum error in Blenderunits to allow - distance",
                                        min=0,
                                        soft_min=0,
                                        default=0.0)
    degreeOut = IntProperty(name="degree",
                            min=3, soft_min=3,
                            max=7, soft_max=7,
                            default=5,
                            description="degree of new curve")
    dis_error = FloatProperty(name="distance error",
                                        description="maximum error in Blenderunits to allow - distance",
                                        min=0,
                                        soft_min=0,
                                        default=0.0)
    keepShort = BoolProperty(name="keep short Splines",
                                        description="keep short splines (less then 7 points)",
                                        default=True)

    def draw(self, context):
        props = self.properties
        layout = self.layout
        col = layout.column()
        col.label('Mode:')
        col.prop(props, 'mode', expand=True)
        if self.properties.mode == 'distance':
            box = layout.box()
            box.label(props.mode, icon='ARROW_LEFTRIGHT')
            box.prop(props, 'error', expand=True)
        if self.properties.mode == 'curvature':
            box = layout.box()
            box.label('degree', icon='SMOOTHCURVE')
            box.prop(props, 'pointsNr', expand=True)
            box.label('threshold', icon='PARTICLE_PATH')
            box.prop(props, 'k_thresh', expand=True)
            box.label('distance', icon='ARROW_LEFTRIGHT')
            box.prop(props, 'dis_error', expand=True)
        col = layout.column()
        col.separator()
        col.prop(props, 'output', text='Output', icon='OUTLINER_OB_CURVE')
        if props.output == 'NURBS':
            col.prop(props, 'degreeOut', expand=True)
        col.prop(props, 'keepShort', expand=True)

    ## Check for curve
    def poll(self, context):
        obj = context.active_object
        return (obj and obj.type == 'CURVE')

    ## execute
    def execute(self, context):
        #print("------START------")

        options = [
self.properties.mode,       #0
self.properties.output,     #1
self.properties.k_thresh,   #2
self.properties.pointsNr,   #3
self.properties.error,      #4
self.properties.degreeOut,  #5
self.properties.dis_error,  #6
self.properties.keepShort]  #7


        bpy.context.user_preferences.edit.global_undo = False

        bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
        obj = context.active_object

        main(context, obj, options)

        bpy.context.user_preferences.edit.global_undo = True

        #print("-------END-------")
        return {'FINISHED'}

#################################################
#### REGISTER ###################################
#################################################
def register():
    bpy.types.register(CURVE_OT_simplify)

def unregister():
    bpy.types.unregister(CURVE_OT_simplify)

if __name__ == "__main__":
    register()