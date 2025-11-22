import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import './App.css';

import Navbar from './components/Navbar';
import Home from './components/Home';
import About from './components/About';
import Projects from './components/Projects';
import Contact from './components/Contact';
import Services from './components/Services';
import Resume from './components/Resume';

// Available transition styles
const TRANSITION_STYLES = {
  fade: 'fade',
  slide: 'slide',
  zoom: 'zoom',
  cube: 'cube',
  flip: 'flip',
  bounce: 'bounce'
};

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const [transitionStyle, setTransitionStyle] = useState(() => {
    return localStorage.getItem('transitionStyle') || 'bounce';
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    document.body.classList.toggle('dark-mode', darkMode);
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('transitionStyle', transitionStyle);
  }, [transitionStyle]);

  return (
    <div className={`App ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <Router>
        <TransitionWrapper transitionStyle={transitionStyle}>
          <Navbar 
            darkMode={darkMode} 
            setDarkMode={setDarkMode}
            transitionStyle={transitionStyle}
            setTransitionStyle={setTransitionStyle}
          />
          <RoutesWithTransitions />
        </TransitionWrapper>
      </Router>
    </div>
  );
}

// Transition Wrapper Component
function TransitionWrapper({ children, transitionStyle }) {
  const location = useLocation();
  
  return (
    <div 
      key={location.pathname} 
      className={`page-transition-container ${transitionStyle}-transition`}
    >
      {children}
    </div>
  );
}

// Routes Component
function RoutesWithTransitions() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/services" element={<Services />} />
      <Route path="/resume" element={<Resume />} />
      <Route path="/projects" element={<Projects />} />
      <Route path="/contact" element={<Contact />} />
    </Routes>
  );
}

export default App;