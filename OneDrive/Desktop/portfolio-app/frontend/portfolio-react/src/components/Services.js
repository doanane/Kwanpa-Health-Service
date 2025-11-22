import React from 'react';


const ComponentName = () => {
  return (
    <div className="page-container component-name-page">
      {/* Video Background */}
      <div className="video-background"></div>
      
      <div className="container">
        {/* Your page content */}
        <div className="row">
          <div className="col-12">
            <h1>Page Title</h1>
            {/* Rest of your content */}
          </div>
        </div>
      </div>
    </div>
  );
};

const Services = () => {
  const services = [
    {
      icon: 'bi-laptop',
      title: 'Full-Stack Development',
      description: 'End-to-end web application development using modern technologies like React, Node.js, and Python frameworks.',
      features: ['Custom Web Applications', 'RESTful APIs', 'Database Design', 'Performance Optimization']
    },
    {
      icon: 'bi-phone',
      title: 'Mobile App Development',
      description: 'Cross-platform mobile applications development using React Native for iOS and Android platforms.',
      features: ['React Native Apps', 'UI/UX Design', 'App Store Deployment', 'Cross-Platform Solutions']
    },
    {
      icon: 'bi-shield-check',
      title: 'Cybersecurity Solutions',
      description: 'Security assessment, penetration testing, and implementation of robust security measures for applications.',
      features: ['Security Audits', 'Penetration Testing', 'Security Protocols', 'Data Protection']
    },
    {
      icon: 'bi-cloud',
      title: 'Cloud & DevOps',
      description: 'Cloud infrastructure setup, deployment automation, and CI/CD pipeline implementation using AWS and Docker.',
      features: ['AWS Services', 'Docker Containers', 'CI/CD Pipelines', 'Server Management']
    },
    {
      icon: 'bi-database',
      title: 'Database Management',
      description: 'Database design, optimization, and management using SQL and NoSQL database systems.',
      features: ['Database Design', 'Performance Tuning', 'Data Migration', 'Backup Solutions']
    },
    {
      icon: 'bi-gear',
      title: 'API Development',
      description: 'Design and development of robust, scalable RESTful APIs and GraphQL endpoints.',
      features: ['REST APIs', 'GraphQL', 'API Documentation', 'Third-party Integrations']
    }
  ];

  return (
    <div className="page-container services-page">
      <div className="video-background">
        <div className="video-overlay"></div>
      </div>
      
      <div className="container mt-5 pt-5">
        <div className="row">
          <div className="col-lg-10 mx-auto">
            <div className="page-header text-center mb-5">
              <h1 className="display-4 fw-bold text-light mb-4">My Services</h1>
              <p className="lead text-light opacity-75">
                Comprehensive software development and cybersecurity solutions
              </p>
            </div>

            <div className="services-grid">
              <div className="row g-4">
                {services.map((service, index) => (
                  <div key={index} className="col-lg-4 col-md-6">
                    <div className="service-card glass-effect p-4 h-100">
                      <div className="service-icon mb-4">
                        <i className={`bi ${service.icon} display-4 text-primary`}></i>
                      </div>
                      <h3 className="service-title text-light mb-3">{service.title}</h3>
                      <p className="service-description text-light opacity-75 mb-4">
                        {service.description}
                      </p>
                      <div className="service-features">
                        <h6 className="text-warning mb-3">Key Features:</h6>
                        <ul className="features-list">
                          {service.features.map((feature, featureIndex) => (
                            <li key={featureIndex} className="text-light opacity-75 mb-2">
                              <i className="bi bi-check-circle-fill text-success me-2"></i>
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Call to Action */}
            <div className="cta-section text-center mt-5 pt-5">
              <div className="glass-effect p-5 rounded-4">
                <h2 className="text-light mb-4">Ready to Start Your Project?</h2>
                <p className="text-light opacity-75 mb-4">
                  Let's work together to bring your ideas to life with cutting-edge technology solutions.
                </p>
                <a href="/contact" className="btn btn-primary btn-lg px-5">
                  <i className="bi bi-send me-2"></i>
                  Get In Touch
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Services;