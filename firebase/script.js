  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional

  const now = new Date();


  var firebaseConfig = {
    apiKey: "AIzaSyBkpEDGlj06SVpYzIbNr2KCIGfYhXBGysE",
    authDomain: "create-active-inertia.firebaseapp.com",
    databaseURL: "https://create-active-inertia-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "create-active-inertia",
    storageBucket: "create-active-inertia.appspot.com",
    messagingSenderId: "210630963199",
    appId: "1:210630963199:web:8c861d8c3f52ef6a9981ca",
    measurementId: "G-FBEK63TEW5"
  };


  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  firebase.analytics();

  //add data
  // var event = "";
  // bool failure = false;


  // failure = true;
  // if failure = true{
  //   event = "frequency";
  // };

  var hours = now.getHours();
  var minutes = now.getMinutes();
  var time_now = hours + "" + ":" + "" + minutes;


  let obj = {
    type_of_event: 'frequency',
    duration_time: '0.5s',
    device_id: (Math.floor(Math.random() * 10000)),
    time: time_now
  }
  firebase.database().ref('inertia_event/' + time_now).set(obj)

// add connection ot c++ app to populate values for nerus

    let neru = {
    device_id: (Math.floor(Math.random() * 10000)),
    location: '51.5074,0.1278',
    name: 'London',
    port: 5683,
    status: 'online'
  }
  firebase.database().ref('neru_status/london').set(neru)

    let neru_coap = {
    device_id: (Math.floor(Math.random() * 10000)),
    location: '51.5074,0.1278',
    current_IP: '176.123.56.7',
    port: 5683,
    status: 'online'
  }
  firebase.database().ref('neru_coap/newcastle').set(neru_coap)


  // const preObject = document.getElementById('object');

  // const dbRefObject = firebase.database().ref().child('object');

  // dbRefObject.on('value', snap => console.log(snap.val()));