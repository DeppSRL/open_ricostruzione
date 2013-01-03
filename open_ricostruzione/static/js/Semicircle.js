/**
 * Semicircle extension for L.Circle.
 * Jan Pieter Waagmeester <jieter@jieter.nl>
 */

/*jshint browser:true, strict:false, globalstrict:false, indent:4, white:true, smarttabs:true*/
/*global L:true*/

L.Circle = L.Circle.extend({
    options: {
        startAngle: 0,
        stopAngle: 359.9999
    },

    // make sure 0 degrees is up (North) and convert to radians.
    startAngle: function () {
        return (this.options.startAngle - 90) * L.LatLng.DEG_TO_RAD;
    },
    stopAngle: function () {
        return (this.options.stopAngle - 90) * L.LatLng.DEG_TO_RAD;
    },

    //rotate point x,y+r around x,y with angle.
    rotated: function (angle, r) {
        return this._point.add(
            L.point(Math.cos(angle), Math.sin(angle)).multiplyBy(r)
        ).round();
    },
    getPathString: function () {

        var center = this._point,
            r = this._radius;

        var start = this.rotated(this.startAngle(), r),
            end = this.rotated(this.stopAngle(), r);

        if (this._checkIfEmpty()) {
            return '';
        }

        if (L.Browser.svg) {

//          STE
// if startA=0 & stopA=360 draws a full circle. BUG FIX

            if(this.options.startAngle == 0 && this.options.stopAngle>359){
                var e = this._point, t = this._radius;
                return "M" + e.x + "," + (e.y - t) + "A" + t + "," + t + ",0,1,1," + (e.x - .1) + "," + (e.y - t) + " z";
            }
            var largeArc = (this.options.stopAngle - this.options.startAngle >= 180) ? '1' : '0';
            //move to center
            var ret = "M" + center.x + "," + center.y;
            //lineTo point on circle startangle from center
            ret += "L " + start.x + "," + start.y;
            //make circle from point start - end:
            ret += "A " + r + "," + r + ",0," + largeArc + ",1," + end.x + "," + end.y + " z";

            return ret;
        } else {
            //TODO: fix this for semicircle...
            center._round();
            r = Math.round(r);
            return "A " + center.x + "," + center.y + " " + r + "," + r + " 0," + (65535 * 360);
        }
    },
    setStartAngle: function (angle) {
        this.options.startAngle = angle;
        return this.redraw();
    },
    setStopAngle: function (angle) {
        this.options.stopAngle = angle;
        return this.redraw();
    },
    setDirection: function (direction, degrees) {
        if (degrees === undefined) {
            degrees = 10;
        }
        this.options.startAngle = direction - (degrees / 2);
        this.options.stopAngle = direction + (degrees / 2);

        return this.redraw();
    }
});
L.Circle.include(!L.Path.CANVAS ? {} : {
    _drawPath: function () {

        var center = this._point,
            r = this._radius;

        var start = this.rotated(this.startAngle(), r);

        this._ctx.beginPath();
        this._ctx.moveTo(center.x, center.y);
        this._ctx.lineTo(start.x, start.y);

        this._ctx.arc(center.x, center.y, this._radius, this.startAngle(), this.stopAngle(), false);
        this._ctx.lineTo(center.x, center.y);
    }

    // _containsPoint: function (p) {
    // TODO: fix for semicircle.
    // var center = this._point,
    //     w2 = this.options.stroke ? this.options.weight / 2 : 0;

    //  return (p.distanceTo(center) <= this._radius + w2);
    // }
});
