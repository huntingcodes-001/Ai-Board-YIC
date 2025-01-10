import logo from './logo.svg';
import './App.css';
import React from 'react';
import Whiteboard from './Whiteboard';
import {Routes,Route} from 'react-router-dom'
import AdminLogin from './AdminLogin';
import StudentLogin from './StudentLogin';
import StudentRegister from "./StudentRegister"
import QNAScript from './QNAScript';
import Process from './Process'
import Summary from './Summary';
import RecordView from "./TestingRecording";


function App() {
  return (
    <>
    <Routes>
      <Route path="/" element={<Whiteboard/>}/>
      <Route path="/adminlogin" element={<AdminLogin/>}/>
      {/* <Route path="/studentlogin" element={<StudentLogin/>}/> */}
      <Route path="/test" element={<RecordView/>}/>
      <Route path="/qna" element={<QNAScript/>}/>
      <Route path="/process" element={<Process/>}/>
      <Route path="/summarize" element={<Summary/>}/>

    </Routes>
    
    </>
  );
}

export default App;
