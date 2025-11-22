import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const API_BASE = 'http://localhost:8000/api';

const Home = () => {
  const [profile, setProfile] = useState(null);
  const [visitorCount, setVisitorCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const videoRef = useRef(null);

  useEffect(() => {
    loadProfile();
    loadVisitorCount();
    
    // Ensure video plays
    if (videoRef.current) {
      videoRef.current.play().catch(error => {
        console.log('Video autoplay failed:', error);
      });
    }
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/profile`);
      setProfile(response.data);
    } catch (err) {
      console.error('Error loading profile:', err);
      setProfile({
        name: "Desmond Opoku Anane",
        title: "Software Engineer & Cybersecurity Analyst",
        email: "anane365221@gmail.com",
        phone: "+233 (0) 554640252",
        location: "Accra, Ghana",
        bio: "Full-stack developer specializing in creating scalable web applications and secure systems. Passionate about innovative solutions and cutting-edge technology.",
        experience: "2+ years",
        skills: ["React Native", "Python", "FastAPI", "Django", "TypeScript", "Node.js", "MySQL", "MongoDB", "AWS", "Cybersecurity"]
      });
    } finally {
      setLoading(false);
    }
  };

  const loadVisitorCount = async () => {
    try {
      const response = await axios.get(`${API_BASE}/visitor-count`);
      setVisitorCount(response.data.visitor_count);
    } catch (err) {
      console.error('Error loading visitor count:', err);
    }
  };

  const downloadCV = () => {
    const link = document.createElement('a');
    link.href = '/DOA_Resume.pdf';
    link.download = 'Desmond_Opoku_Anane_CV.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const stats = [
    { number: "2+", label: "Years Experience", icon: "bi-briefcase" },
    { number: "15+", label: "Projects Completed", icon: "bi-folder" },
    { number: "12+", label: "Technologies", icon: "bi-gear" },
    { number: "600+", label: "Code Commits", icon: "bi-git" }
  ];

  if (loading) {
    return (
      <div className="min-vh-100 d-flex align-items-center justify-content-center bg-dark text-white">
        <div className="text-center">
          <div className="loading-spinner mb-4"></div>
          <h3 className="typewriter">Initializing Portfolio...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="home-page">
      {/* Video Background */}
      <div className="video-background">
        <video
          ref={videoRef}
          autoPlay
          muted
          loop
          playsInline
          className="background-video"
          poster="https://images.unsplash.com/photo-1555066931-4365d14bab8c?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
        >
          <source src="https://assets.mixkit.co/videos/preview/mixkit-white-flowers-against-a-moving-coding-background-47236-large.mp4" type="video/mp4" />
          <source src="https://cdn.pixabay.com/video/2023/02/28/160456-806503141_large.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className="video-overlay"></div>
      </div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="row align-items-center min-vh-100">
            <div className="col-lg-6">
              <div className="hero-content">
                <div className="intro-text mb-4">
                  <span className="greeting">Hello, I'm</span>
                  <h1 className="main-name">
                    <span className="first-name">Desmond</span>
                    <span className="last-name"> Opoku Anane</span>
                  </h1>
                  <div className="title-container">
                    <h2 className="job-title">
                      <span className="title-part">Software Engineer</span>
                      <span className="title-separator"> & </span>
                      <span className="title-part">Cybersecurity Analyst</span>
                    </h2>
                  </div>
                </div>

                <p className="hero-description">
                  I specialize in building scalable web applications and secure systems. 
                  With expertise in full-stack development and cybersecurity, I create 
                  robust solutions that drive business success.
                </p>

                <div className="contact-details mb-4">
                  <div className="contact-item">
                    <i className="bi bi-telephone-fill"></i>
                    <span>+233 (0) 554640252</span>
                  </div>
                  <div className="contact-item">
                    <i className="bi bi-geo-alt-fill"></i>
                    <span>Accra, Ghana</span>
                  </div>
                  <div className="contact-item">
                    <i className="bi bi-envelope-fill"></i>
                    <span>anane365221@gmail.com</span>
                  </div>
                </div>

                <div className="action-buttons">
                  <button className="btn btn-primary btn-download" onClick={downloadCV}>
                    <i className="bi bi-download me-2"></i>
                    Download CV
                  </button>
                  <Link to="/contact" className="btn btn-outline-light btn-hire">
                    <i className="bi bi-send me-2"></i>
                    Hire Me
                  </Link>
                </div>

                <div className="social-links">
                  <a href="https://www.linkedin.com/in/desmond-opoku-anane-39b5412b4/" target="_blank" rel="noopener noreferrer">
                    <i className="bi bi-linkedin"></i>
                  </a>
                  <a href="https://github.com/doanane" target="_blank" rel="noopener noreferrer">
                    <i className="bi bi-github"></i>
                  </a>
                  <a href="https://twitter.com/yourusername" target="_blank" rel="noopener noreferrer">
                    <i className="bi bi-twitter"></i>
                  </a>
                  <a href="mailto:anane365221@gmail.com">
                    <i className="bi bi-envelope"></i>
                  </a>
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="profile-animation-section">
                <div className="rotating-ring">
                  <div className="ring ring-1"></div>
                  <div className="ring ring-2"></div>
                  <div className="ring ring-3"></div>
                </div>
                <div className="profile-container">
                  <div className="animated-logo">
                    <div className="logo-body">
                      <div className="head"></div>
                      <div className="body"></div>
                      <div className="arm left-arm"></div>
                      <div className="arm right-arm"></div>
                      <div className="leg left-leg"></div>
                      <div className="leg right-leg"></div>
                    </div>
                    <div className="tech-elements">
                      <div className="code-line line-1"></div>
                      <div className="code-line line-2"></div>
                      <div className="code-line line-3"></div>
                      <div className="floating-dot dot-1"></div>
                      <div className="floating-dot dot-2"></div>
                      <div className="floating-dot dot-3"></div>
                    </div>
                  </div>
                </div>
                <div className="status-indicator">
                  <div className="pulse-dot"></div>
                  <span>Available for work</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            {stats.map((stat, index) => (
              <div key={index} className="stat-item">
                <div className="stat-icon">
                  <i className={`bi ${stat.icon}`}></i>
                </div>
                <div className="stat-content">
                  <div className="stat-number">{stat.number}</div>
                  <div className="stat-label">{stat.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;