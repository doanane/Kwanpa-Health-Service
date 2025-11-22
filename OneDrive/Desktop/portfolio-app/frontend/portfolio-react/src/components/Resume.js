import React from 'react';

const Resume = () => {
  const experiences = [
    {
      period: 'September 2025 – November 2025',
      role: 'Software Engineer Intern',
      company: 'Amalitech',
      description: 'Developed microservices using Java for internal training applications. Built FastAPI-based backend services including authentication and user management.',
      achievements: [
        'Developed FastAPI microservices for internal applications',
        'Built and maintained Django REST APIs',
        'Implemented asynchronous API endpoints',
        'Collaborated in Agile development environment'
      ]
    },
    {
      period: 'October 2024 – February 2025',
      role: 'Software Engineer',
      company: 'GETA Solutions',
      description: 'Contributed to full lifecycle development of company website using React, Node.js, Express.js, and MongoDB.',
      achievements: [
        'Engineered frontend for Services, Careers, and Publications pages',
        'Developed robust backend architecture with user authentication',
        'Managed website hosting and performance optimization',
        'Built RESTful API endpoints for data management'
      ]
    },
    {
      period: 'February 2025',
      role: 'Fullstack Developer Intern',
      company: 'aeTech Hub, Accra',
      description: 'Engineered user interface components for Tarmove logistics company using Next.js.',
      achievements: [
        'Built Get Started page for user interaction',
        'Developed Sign Up and Login pages for Shipper and Transporter functionalities',
        'Implemented responsive UI components'
      ]
    },
    {
      period: 'March 2024 – February 2025',
      role: 'Software Engineer (DevOps)',
      company: 'Youth Space Africa (YOSA)',
      description: 'Contributed to website development and backend services for non-profit organization.',
      achievements: [
        'Hosted and maintained organization website',
        'Engineered API endpoints for aid requests management',
        'Implemented role-based authorization system',
        'Ensured secure data handling and processing'
      ]
    }
  ];

  const skills = [
    { name: 'React & React Native', level: 90 },
    { name: 'Python & FastAPI', level: 88 },
    { name: 'JavaScript/TypeScript', level: 85 },
    { name: 'Node.js & Express', level: 82 },
    { name: 'MongoDB & MySQL', level: 80 },
    { name: 'AWS & Cloud Services', level: 75 },
    { name: 'Docker & DevOps', level: 70 },
    { name: 'Cybersecurity', level: 78 }
  ];

  return (
    <div className="page-container resume-page">
      <div className="video-background">
        <div className="video-overlay"></div>
      </div>
      
      <div className="container mt-5 pt-5">
        <div className="row">
          <div className="col-lg-10 mx-auto">
            <div className="page-header text-center mb-5">
              <h1 className="display-4 fw-bold text-light mb-4">My Resume</h1>
              <p className="lead text-light opacity-75">
                Professional experience and technical expertise
              </p>
            </div>

            {/* Skills Section */}
            <div className="skills-section mb-5">
              <h2 className="text-light mb-4">Technical Skills</h2>
              <div className="row">
                {skills.map((skill, index) => (
                  <div key={index} className="col-lg-6 mb-4">
                    <div className="skill-item">
                      <div className="d-flex justify-content-between mb-2">
                        <span className="text-light fw-semibold">{skill.name}</span>
                        <span className="text-primary">{skill.level}%</span>
                      </div>
                      <div className="progress" style={{ height: '8px' }}>
                        <div 
                          className="progress-bar" 
                          role="progressbar" 
                          style={{ width: `${skill.level}%` }}
                          aria-valuenow={skill.level}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Experience Section */}
            <div className="experience-section">
              <h2 className="text-light mb-4">Work Experience</h2>
              <div className="timeline">
                {experiences.map((exp, index) => (
                  <div key={index} className="timeline-item mb-5">
                    <div className="timeline-card glass-effect p-4">
                      <div className="timeline-header mb-3">
                        <div className="d-flex justify-content-between align-items-start flex-wrap">
                          <div>
                            <h4 className="text-light mb-1">{exp.role}</h4>
                            <h5 className="text-primary mb-2">{exp.company}</h5>
                          </div>
                          <span className="badge bg-warning text-dark">{exp.period}</span>
                        </div>
                      </div>
                      <p className="text-light opacity-75 mb-3">{exp.description}</p>
                      <div className="achievements">
                        <h6 className="text-warning mb-2">Key Achievements:</h6>
                        <ul className="achievements-list">
                          {exp.achievements.map((achievement, achievementIndex) => (
                            <li key={achievementIndex} className="text-light opacity-75 mb-1">
                              {achievement}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Download Resume */}
            <div className="download-section text-center mt-5">
              <div className="glass-effect p-4 rounded-4">
                <h3 className="text-light mb-3">Download Full Resume</h3>
                <p className="text-light opacity-75 mb-4">
                  Get the complete version of my resume with detailed project information and references.
                </p>
                <button 
                  className="btn btn-primary btn-lg"
                  onClick={() => document.getElementById('cv-download').click()}
                >
                  <i className="bi bi-download me-2"></i>
                  Download PDF Resume
                </button>
                <a id="cv-download" href="/DOA_Resume.pdf" download className="d-none"></a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Resume;