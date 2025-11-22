import React from 'react';

const About = () => {
  const skills = [
    { category: "Frontend", items: ["React", "React Native", "TypeScript", "HTML5", "CSS3", "Bootstrap"] },
    { category: "Backend", items: ["Python", "FastAPI", "Django", "Node.js", "Express.js"] },
    { category: "Databases", items: ["MongoDB", "MySQL", "PostgreSQL", "SQL"] },
    { category: "DevOps & Cloud", items: ["AWS", "Docker", "Git", "CI/CD"] },
    { category: "Cybersecurity", items: ["Cyber Operations", "Penetration Testing", "Security Analysis"] },
    { category: "Tools", items: ["VS Code", "Postman", "Figma", "Jira", "Linux"] }
  ];

  return (
    <div className="page-container about-page">
      <div className="video-background">
        <div className="video-overlay"></div>
      </div>
      
      <div className="container mt-5 pt-5">
        <div className="row">
          <div className="col-lg-10 mx-auto">
            <div className="page-header text-center mb-5">
              <h1 className="display-4 fw-bold text-light mb-4">About Me</h1>
              <p className="lead text-light opacity-75">
                Passionate Software Engineer & Cybersecurity Analyst
              </p>
            </div>

            <div className="about-content">
              <div className="row">
                <div className="col-lg-6 mb-5">
                  <div className="about-card glass-effect p-4 h-100">
                    <h3 className="text-primary mb-4">My Journey</h3>
                    <p className="text-light mb-4">
                      I am a Software Engineer and Cybersecurity Analyst committed to advancing my career 
                      in software development by working collaboratively with motivated, results-driven teams 
                      within dynamic and structured organizational environments.
                    </p>
                    <p className="text-light mb-4">
                      My goal is to leverage my expertise in both frontend and backend technologies to 
                      contribute meaningfully to organizational growth while driving innovation and 
                      delivering high-impact solutions.
                    </p>
                    <p className="text-light">
                      As a dedicated Computer Science professional, I aim to leverage my technical skills 
                      and knowledge to contribute to innovative projects and gain hands-on experience in 
                      software development, system design, and IT infrastructure.
                    </p>
                  </div>
                </div>

                <div className="col-lg-6 mb-5">
                  <div className="about-card glass-effect p-4 h-100">
                    <h3 className="text-primary mb-4">Education & Background</h3>
                    <div className="education-item mb-4">
                      <h5 className="text-warning">Computer Science</h5>
                      <p className="text-light mb-2">Bachelor's Degree</p>
                      <p className="text-muted">Relevant Coursework: Data Structures, Algorithms, Java, Python, 
                      Database Management, AI, Web Development, Cybersecurity</p>
                    </div>
                    <div className="education-item">
                      <h5 className="text-warning">Professional Certifications</h5>
                      <p className="text-light">Full Stack Web Development, AWS Cloud Practitioner</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Skills Section */}
              <div className="skills-section mt-5">
                <h2 className="text-center text-light mb-5">Technical Skills</h2>
                <div className="row">
                  {skills.map((skillGroup, index) => (
                    <div key={index} className="col-lg-4 col-md-6 mb-4">
                      <div className="skill-category-card glass-effect p-4 h-100">
                        <h4 className="text-primary mb-3">{skillGroup.category}</h4>
                        <div className="skills-list">
                          {skillGroup.items.map((skill, skillIndex) => (
                            <span key={skillIndex} className="skill-tag">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;