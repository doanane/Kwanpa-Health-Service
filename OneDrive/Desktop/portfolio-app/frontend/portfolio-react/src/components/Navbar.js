import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const TRANSITION_STYLES = [
  { value: 'fade', label: 'Fade', icon: 'bi-circle' },
  { value: 'slide', label: 'Slide', icon: 'bi-arrow-right' },
  { value: 'zoom', label: 'Zoom', icon: 'bi-zoom-in' },
  { value: 'cube', label: 'Cube', icon: 'bi-box' },
  { value: 'flip', label: 'Flip', icon: 'bi-arrow-repeat' },
  { value: 'bounce', label: 'Bounce', icon: 'bi-arrow-down' }
];

const Navbar = ({ darkMode, setDarkMode, transitionStyle, setTransitionStyle }) => {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [showTransitionMenu, setShowTransitionMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/services', label: 'Services' },
    { path: '/resume', label: 'Resume' },
    { path: '/projects', label: 'Work' },
    { path: '/contact', label: 'Contact' }
  ];

  return (
    <nav className={`navbar navbar-expand-lg navbar-dark fixed-top ${scrolled ? 'scrolled' : ''}`}>
      <div className="container">
        <Link className="navbar-brand fw-bold d-flex align-items-center" to="/">
          <div className="bg-warning rounded p-2 me-2">
            <i className="bi bi-code-slash text-dark"></i>
          </div>
          <span>Desmond.</span>
        </Link>
        
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span className="navbar-toggler-icon"></span>
        </button>
        
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            {navItems.map((item) => (
              <li key={item.path} className="nav-item">
                <Link 
                  className={`nav-link ${location.pathname === item.path ? 'active text-warning' : ''}`} 
                  to={item.path}
                >
                  {item.label}
                </Link>
              </li>
            ))}
            
            {/* Transition Style Selector */}
            <li className="nav-item dropdown">
              <button 
                className="btn theme-toggle ms-2"
                onClick={() => setShowTransitionMenu(!showTransitionMenu)}
                title="Change Transition Style"
              >
                <i className="bi bi-magic"></i>
              </button>
              {showTransitionMenu && (
                <div className="dropdown-menu show" style={{display: 'block', position: 'absolute', right: 0}}>
                  {TRANSITION_STYLES.map(style => (
                    <button
                      key={style.value}
                      className={`dropdown-item ${transitionStyle === style.value ? 'active' : ''}`}
                      onClick={() => {
                        setTransitionStyle(style.value);
                        setShowTransitionMenu(false);
                      }}
                    >
                      <i className={`${style.icon} me-2`}></i>
                      {style.label}
                    </button>
                  ))}
                </div>
              )}
            </li>

            {/* Dark Mode Toggle */}
            <li className="nav-item">
              <button 
                className="btn theme-toggle ms-2"
                onClick={toggleDarkMode}
                title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                <i className={`bi ${darkMode ? 'bi-sun-fill' : 'bi-moon-fill'}`}></i>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;