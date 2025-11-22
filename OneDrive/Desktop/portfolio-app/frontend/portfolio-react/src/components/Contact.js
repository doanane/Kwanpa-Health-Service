import axios from 'axios';
import { useState } from 'react';

const API_BASE = 'http://localhost:8000/api';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setSubmitError(''); 
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError('');

    try {
      const response = await axios.post(`${API_BASE}/contact`, formData);
      
      setSubmitted(true);
      setFormData({ name: '', email: '', message: '' });
      
      console.log('Contact form submitted successfully:', response.data);
      
    } catch (err) {
      console.error('Error sending message:', err);
      
      if (err.response && err.response.data && err.response.data.detail) {
        setSubmitError(`Error: ${err.response.data.detail}`);
      } else if (err.code === 'NETWORK_ERROR' || err.message.includes('Network Error')) {
        setSubmitError('Network error: Please check if the backend server is running on port 8000');
      } else {
        setSubmitError('Error sending message. Please try again or email me directly at anane365221@gmail.com');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container contact-page">
      <div className="video-background"></div>
      
      <div className="container mt-5 pt-5">
        <div className="row justify-content-center">
          <div className="col-lg-10">
            <div className="page-header text-center mb-5">
              <h1 className="display-4 fw-bold text-light mb-4">Contact Me</h1>
              <p className="lead text-light opacity-75">
                Get in touch to discuss your project or opportunity
              </p>
            </div>

            <div className="row">
              <div className="col-lg-8">
                {submitted && (
                  <div className="alert alert-success alert-dismissible fade show" role="alert">
                    <strong> Thank you!</strong> Your message has been sent successfully. I'll get back to you soon!
                    <button type="button" className="btn-close" onClick={() => setSubmitted(false)}></button>
                  </div>
                )}

                {submitError && (
                  <div className="alert alert-warning alert-dismissible fade show" role="alert">
                    <strong> Notice:</strong> {submitError}
                    <button type="button" className="btn-close" onClick={() => setSubmitError('')}></button>
                  </div>
                )}

                <div className="contact-form glass-effect p-4 rounded-4 mb-4">
                  <form onSubmit={handleSubmit}>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label className="form-label text-light">Your Name *</label>
                        <input
                          type="text"
                          className="form-control"
                          name="name"
                          value={formData.name}
                          onChange={handleChange}
                          required
                          disabled={submitting}
                        />
                      </div>
                      <div className="col-md-6 mb-3">
                        <label className="form-label text-light">Email Address *</label>
                        <input
                          type="email"
                          className="form-control"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          required
                          disabled={submitting}
                        />
                      </div>
                    </div>
                    <div className="mb-4">
                      <label className="form-label text-light">Your Message *</label>
                      <textarea
                        className="form-control"
                        rows="6"
                        name="message"
                        value={formData.message}
                        onChange={handleChange}
                        required
                        disabled={submitting}
                        placeholder="Tell me about your project or how I can help you..."
                      ></textarea>
                    </div>
                    <button 
                      type="submit" 
                      className="btn btn-primary btn-lg w-100 py-3"
                      disabled={submitting}
                    >
                      {submitting ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Sending Message...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-send me-2"></i>
                          Send Message
                        </>
                      )}
                    </button>
                  </form>
                </div>
              </div>

              <div className="col-lg-4">
                <div className="contact-info-section">
                  <h4 className="text-center mb-4">Contact Information</h4>
                  
                  <div className="contact-item">
                    <i className="bi bi-envelope-fill"></i>
                    <div className="contact-details">
                      <span className="contact-label">Email</span>
                      <span className="contact-value">
                        <a href="mailto:anane365221@gmail.com">anane365221@gmail.com</a>
                      </span>
                    </div>
                  </div>

                  <div className="contact-item">
                    <i className="bi bi-geo-alt-fill"></i>
                    <div className="contact-details">
                      <span className="contact-label">Location</span>
                      <span className="contact-value">Accra, Ghana</span>
                    </div>
                  </div>

                  <div className="contact-item">
                    <i className="bi bi-telephone-fill"></i>
                    <div className="contact-details">
                      <span className="contact-label">Phone</span>
                      <span className="contact-value phone-number">+233 554 64 0252</span>
                    </div>
                  </div>

                  <div className="direct-email mt-4 p-3 rounded text-center">
                    <p className="text-light mb-2">Prefer to email directly?</p>
                    <a 
                      href="mailto:anane365221@gmail.com?subject=Portfolio Inquiry&body=Hello Desmond, I'm interested in..."
                      className="btn btn-outline-light btn-sm"
                    >
                      <i className="bi bi-envelope me-2"></i>
                      Open Email Client
                    </a>
                  </div>

                  <div className="social-links mt-4 text-center">
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
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;