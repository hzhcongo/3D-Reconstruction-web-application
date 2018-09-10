$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');

        //if($('#sidebar').hasClass('active')){
        //    newsize = $('#modelviewer').first().first().width() + 200;
        //}
        //else{
        //    newsize = $('#modelviewer').first().first().width() - 200;
        //}
        //    $('#modelviewer').first().first().attr('width', newsize);
    });

    {% if name %}
    $('#switchControl').on('click', switchControlMode);
    $('#cutBase').on('click', cutBase);

    $('#plyASCII').on('click', function() {
        generateModelLink(0);
    });
    $('#plyBinary').on('click', function() {
        generateModelLink(1);
    });

    $('#stlASCII').on('click', function() {
        generateModelLinkSTL(0);
    });
    $('#stlBinary').on('click', function() {
        generateModelLinkSTL(1);
    });

    $('#objASCII').on('click', function() {
        generateModelLinkOBJ(0);
    });
    $('#objBinary').on('click', function() {
        generateModelLinkOBJ(1);
    });

    {% else %}
    $('#switchControl').on('click', alerter);
    $('#cutBase').on('click', alerter);

    $('#plyASCII').on('click', alerter);
    $('#plyBinary').on('click', alerter);

    $('#stlASCII').on('click', alerter);
    $('#stlBinary').on('click', alerter);

    $('#objASCII').on('click', alerter);
    $('#objBinary').on('click', alerter);

    $('#linker').on('click', alerter);
    $('#linker2').on('click', alerter);
    {% endif %}
});

function alerter(){
    ezBSAlert({
          type: "alert",
          messageText: "Please select a 3D model to view first!",
          alertType: "primary"
    }).done(function (e) {
    });
}

if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var camera, scene, renderer, tfControl, tbControl;
var geometry, material, mesh;
var floorGeometry, floorMaterial, floorMesh;
var clicking = true;
var isTranslate = false;;
// $( document ).ready(function() {
init();
render();
animate();
// });

function init() {
    container = document.createElement('div');
    document.getElementById("modelviewer").appendChild(container);

    //Renderer
    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setSize( window.innerWidth, window.innerHeight );
    container.appendChild( renderer.domElement );

    //Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xb7b8b6 );
    scene.add( new THREE.GridHelper( 25, 20 ) );

    //Floor
    floorGeometry = new THREE.BoxGeometry(15,0.001,15);
    floorMaterial = new THREE.MeshBasicMaterial( {color: 0x4cb5f5, opacity : 0.5, transparent: true, depthWrite:false} );
    floorMesh = new THREE.Mesh(floorGeometry, floorMaterial);
    floorMesh.position.set(0,0,0);
    scene.add(floorMesh);

    //Camera
    camera = new THREE.PerspectiveCamera(60 , window.innerWidth / window.innerHeight, 1, 1000 );
    camera.position.set(0, 10, 10 );
    camera.lookAt(scene.position);

    //Controls
    tbControl = new THREE.TrackballControls( camera );
    tbControl.rotateSpeed = 0;
    tbControl.zoomSpeed = 1.2;
    tbControl.panSpeed = 0.8;
    tbControl.noZoom = false;
    tbControl.noPan = false;
    tbControl.staticMoving = true;
    tbControl.dynamicDampingFactor = 0.3;
    tbControl.keys = [ 65, 83, 68 ];
    tbControl.addEventListener( 'change', render );

    tfControl = new THREE.TransformControls( camera, renderer.domElement );
    tfControl.addEventListener( 'change', render );

    //PLY file
    {% if name %}

    var loader = new THREE.PLYLoader();
    loader.load( "{{ url_for('static', filename='model/' + name + '.ply')}}", function ( geometry ) {
        console.log(geometry);
        geometry.computeFaceNormals();
        geometry.dynamic  = true;
        geometry.dirty = true;
        geometry.overdraw = true;

        var meshCenter = geometry.boundingSphere.center;
        var meshRadius = geometry.boundingSphere.radius;
        var s = (meshRadius === 0 ? 1 : 1.0 / meshRadius) * 10;
        var m = new THREE.Matrix4().set(
        s, 0, 0, -s*meshCenter.x,
        0, s , 0, -s*meshCenter.y,
        0, 0, s, -s*meshCenter.z,
        0, 0, 0, 1);
        geometry.applyMatrix(m);

        geometry1 = new THREE.Geometry().fromBufferGeometry( geometry );
        console.log(geometry1.toJSON);
        material = new THREE.MeshPhongMaterial( { color: 0xffffff, flatShading: false, vertexColors: THREE.FaceColors} );
        mesh = new THREE.Mesh( geometry1, material );
        scene.add( mesh );
        tfControl.attach(mesh);
        scene.add(tfControl);
        tfControl.setMode("rotate");
        tfControl.setSpace( tfControl.space = "local");
    });

    {% endif %}

    //Lights
    var light = new THREE.DirectionalLight( 0xffffff, 1.5 );
    light.position.set( 1, 1, 1 );
    scene.add( light );
    var light = new THREE.DirectionalLight( 0x002288 );
    light.position.set( -1, -1, -1 );
    scene.add( light );
    var light = new THREE.AmbientLight( 0x222222 );
    scene.add( light );

    document.addEventListener( 'mousedown', onMouseDown );
}

function animate() {

    requestAnimationFrame(animate);
    tbControl.update();
}


function render() {
    tfControl.update();
    renderer.render( scene, camera );
}

function onMouseDown(event){
    event.preventDefault();
    var mouse3D = new THREE.Vector3( ( event.clientX / window.innerWidth ) * 2 - 1,  -( event.clientY / window.innerHeight ) * 2 + 1,  0.5 );
    var raycaster =  new THREE.Raycaster();
    raycaster.setFromCamera( mouse3D, camera );
    var intersects = raycaster.intersectObjects(scene.children);
    for ( var i = 0; i < intersects.length; i++ ) {
        if(intersects[i].object.uuid == mesh.uuid){
            /*if(clicking){
                intersects[ i ].object.material.color.set( 0x96C0B7 );
                clicking = !clicking;
            }
            else{
                intersects[ i ].object.material.color.set( 0xff0000 );
                clicking = !clicking;
            }*/
        }
    }
    render();
    console.log(intersects);
}

function switchControlMode(){
    isTranslate = !isTranslate;
    if(isTranslate){
        tfControl.setMode("translate");
    }
    else{
        tfControl.setMode("rotate");
    }
    return false;
}

function csgSubtract(){
    backGeometry(mesh);
    backGeometry(floorMesh);

    var mesh_bsp = new ThreeBSP(mesh);
    var floorMesh_bsp = new ThreeBSP(floorMesh);
    var result = mesh_bsp.subtract(floorMesh_bsp).toMesh();
    mesh.geometry = result.geometry;
    render();
    return false;
}

function simplify(){
    var modifer = new THREE.SimplifyModifier();
    var simplified = modifer.modify( mesh.geometry, mesh.geometry.vertices.length * 0.5 | 0 );
    console.log(mesh.geometry.vertices.length);
    mesh.geometry = simplified;
    console.log(mesh.geometry.vertices.length);
    render();
    return false;
}

function backGeometry(mesh){
    mesh.updateMatrix();
    mesh.geometry.applyMatrix( mesh.matrix );
    mesh.matrix.identity();
    mesh.position.set( 0, 0, 0 );
    mesh.rotation.set( 0, 0, 0 );
    mesh.scale.set( 1, 1, 1 );
    return false;
}

function cutBase(){
    // console.log(mesh.geometry);
    backGeometry(mesh);
    var vertices = mesh.geometry.vertices;
    var vToDelete = [];
    var collapsePoint=-1;
    var min = 10000;
    for (var i = 0; i <vertices.length; i++) {

        if(vertices[i].y < 0){
            vToDelete.push(i);
        }
        else {
            if(collapsePoint == -1){
                collapsePoint = i;
                min = vertices[i].y-0;
            }
            else{
                var current = vertices[i].y-0;
                if(current < min){
                    collapsePoint = i;
                    min = current;
                }
            }
        }
    }
    console.log(collapsePoint);
    console.log(vToDelete);

    if(collapsePoint!=-1){
        vToDelete.forEach(function(element){
            vertices[element] = vertices[collapsePoint]
        });
    }

    // var faces = mesh.geometry.faces;
    // var fToDelete = [];
    // for (var i = 0; i <faces.length; i++) {
    // 	if(contains(vToDelete, faces['a']) || contains(vToDelete, faces['b']) || contains(vToDelete, faces['c'])){
    // 		fToDelete.push(i);
    // 	}
    // }

    // for (var i = 0; i <vToDelete.length;i++){
    // 	delete mesh.geometry.vertices[vToDelete[i]];
    // }
    // for (var i = 0; i <fToDelete.length;i++){
    // 	delete mesh.geometry.faces[fToDelete[i]];
    // }
    // mesh.geometry.faces = mesh.geometry.faces.filter( function(a){ return a!== undefined });
    // mesh.geometry.vertices = mesh.geometry.vertices.filter( function(a){ return a!== undefined });
    mesh.geometry.elementsNeedUpdate = true;
    render();
    return false;
}

    function generateModelLink(i){

        var exp = new THREE.PLYExporter();
        var endingFile = "_Binary.ply";

        // Process into the ASCII/binary file format
        if (i == 1) {
            var data = exp.parse(mesh, { binary: true });
        }
        else {
            if (confirm("Generating model in ASCII format may not work for big-sized models. Proceed?") == false)
                return false;
            var data = exp.parse(mesh);
            endingFile = "_ASCII.ply";
        }

        var file = new File([data], "generated.ply");
        var a = document.getElementById("linker");
        a.href = URL.createObjectURL(file);

        var currURL = window.location.href.split("/");
        a.download = currURL[currURL.length - 1] + endingFile;


        window.alert("Model updated. Please download and save the model locally. Any changes will not be saved in the web server");
        return false;
    }

    function generateModelLinkSTL(i){
        var exp = new THREE.STLExporter();
        var endingFile = "_Binary.stl";

        // Process into the ASCII/binary file format
        if (i == 1) {
            var data = exp.parse(mesh, { binary: true });
        }
        else {
            if (confirm("Generating model in ASCII format may not work for big-sized models. Proceed?") == false)
                return false;
            var data = exp.parse(mesh);
            endingFile = "_ASCII.stl";
        }

        var file = new File([data], "generated.stl");
        var a = document.getElementById("linker");
        a.href = URL.createObjectURL(file);

        var currURL = window.location.href.split("/");
        a.download = currURL[currURL.length - 1] + endingFile;

        window.alert("Model updated. Please download and save the model locally. Any changes will not be saved in the web server");
        return false;
    }

    function generateModelLinkOBJ(i){
        var exp = new THREE.OBJExporter();
        var endingFile = "_Binary.obj";

        // Process into the ASCII/binary file format
        if (i == 1) {
            var data = exp.parse(mesh, { binary: true });
        }
        else {
            if (confirm("Generating model in ASCII format may not work for big-sized models. Proceed?") == false)
                return false;
            var data = exp.parse(mesh);
            endingFile = "_ASCII.obj";
        }

        var file = new File([data], "generated.obj");
        var a = document.getElementById("linker");
        a.href = URL.createObjectURL(file);

        var currURL = window.location.href.split("/");
        a.download = currURL[currURL.length - 1] + endingFile;

        window.alert("Model updated. Please download and save the model locally. Any changes will not be saved in the web server");
        return false;
    }

    function contains(arr, element) {
        for (var i = 0; i < arr.length; i++) {
            if (arr[i] === element) {
                return true;
            }
        }
        return false;
    }