import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE}/profile`);
      setProjects(response.data.projects || []);
    } catch (err) {
      // Fallback projects based on your experience
      setProjects([
        {
          id: '1',
          name: 'Saloon Connect',
          description: 'A location-based platform connecting customers with nearby salons for easy booking and payments. Built REST APIs with FastAPI for salon discovery, booking, and payments.',
          technologies: ['FastAPI', 'React', 'MongoDB', 'JWT', 'Payment Integration'],
          category: 'fullstack',
          image: 'bi-scissors',
          link: '#'
        },
        {
          id: '2',
          name: 'AWS Employee Reward System',
          description: 'Contributed to development of a global employee rewards monitoring system for AWS, utilizing Next.js for frontend and building interactive data-driven pages.',
          technologies: ['Next.js', 'React', 'REST APIs', 'Data Visualization'],
          category: 'frontend',
          image: 'bi-award',
          link: '#'
        },
        {
          id: '3',
          name: 'CollabSpace - Amalitech',
          description: 'Internal training application with microservices architecture. Developed backend services using Java and FastAPI with authentication and user management.',
          technologies: ['Java', 'FastAPI', 'Microservices', 'Docker', 'CI/CD'],
          category: 'backend',
          image: 'bi-people',
          link: '#'
        },
        {
          id: '4',
          name: 'GETA Solutions Website',
          description: 'Full company website development with React frontend and Node.js/Express backend. Implemented Services, Careers, and Publications sections.',
          technologies: ['React', 'Node.js', 'Express', 'MongoDB', 'REST API'],
          category: 'fullstack',
          image: 'bi-globe',
          link: '#'
        },
        {
          id: '5',
          name: 'Tarmove Logistics',
          description: 'Logistics shipping company platform with Next.js frontend. Developed user authentication and role-based access for Shippers and Transporters.',
          technologies: ['Next.js', 'React', 'TypeScript', 'UI/UX Design'],
          category: 'frontend',
          image: 'bi-truck',
          link: '#'
        },
        {
          id: '6',
          name: 'Youth Space Africa',
          description: 'Non-profit organization website with donation and volunteer management system. Implemented secure API endpoints and role-based authorization.',
          technologies: ['React', 'Node.js', 'MongoDB', 'Cybersecurity', 'Hosting'],
          category: 'fullstack',
          image: 'bi-heart',
          link: '#'
        }
      ]);
    }
  };

  const filters = [
    { key: 'all', label: 'All Projects' },
    { key: 'fullstack', label: 'Full Stack' },
    { key: 'frontend', label: 'Frontend' },
    { key: 'backend', label: 'Backend' }
  ];

  const filteredProjects = activeFilter === 'all' 
    ? projects 
    : projects.filter(project => project.category === activeFilter);

  return (
    <div className="page-container projects-page">
      <div className="video-background">
        <div className="video-overlay"></div>
      </div>
      
      <div className="container mt-5 pt-5">
        <div className="row">
          <div className="col-lg-10 mx-auto">
            <div className="page-header text-center mb-5">
              <h1 className="display-4 fw-bold text-light mb-4">My Projects</h1>
              <p className="lead text-light opacity-75">
                A collection of my recent work and professional projects
              </p>
            </div>

            {/* Project Filters */}
            <div className="filters-section mb-5">
              <div className="d-flex justify-content-center flex-wrap gap-3">
                {filters.map(filter => (
                  <button
                    key={filter.key}
                    className={`btn filter-btn ${activeFilter === filter.key ? 'btn-primary' : 'btn-outline-light'}`}
                    onClick={() => setActiveFilter(filter.key)}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Projects Grid */}
            <div className="projects-grid">
              <div className="row g-4">
                {filteredProjects.map(project => (
                  <div key={project.id} className="col-lg-4 col-md-6">
                    <div className="project-card glass-effect h-100">
                      <div className="project-image">
                        <i className={`bi ${project.image} display-1 text-primary`}></i>
                      </div>
                      <div className="project-content p-4">
                        <h4 className="project-title text-light mb-3">{project.name}</h4>
                        <p className="project-description text-light opacity-75 mb-4">
                          {project.description}
                        </p>
                        <div className="project-technologies mb-4">
                          {project.technologies.map((tech, index) => (
                            <span key={index} className="tech-tag">
                              {tech}
                            </span>
                          ))}
                        </div>
                        <div className="project-actions">
                          <button className="btn btn-outline-light btn-sm me-2">
                            <i className="bi bi-eye me-1"></i>
                            View Demo
                          </button>
                          <button className="btn btn-outline-primary btn-sm">
                            <i className="bi bi-github me-1"></i>
                            Code
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Empty State */}
            {filteredProjects.length === 0 && (
              <div className="text-center py-5">
                <div className="glass-effect p-5 rounded-4">
                  <i className="bi bi-folder-x display-1 text-muted mb-3"></i>
                  <h4 className="text-light mb-3">No projects found</h4>
                  <p className="text-light opacity-75">
                    No projects match the selected filter. Try a different category.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Projects;