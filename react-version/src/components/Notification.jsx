import './Notification.css';

export default function Notification({ message, type, isVisible, onClose }) {
  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'success': return 'fas fa-check-circle';
      case 'error': return 'fas fa-exclamation-triangle';
      case 'info': return 'fas fa-info-circle';
      case 'warning': return 'fas fa-exclamation-circle';
      default: return 'fas fa-info-circle';
    }
  };

  return (
    <div className={`notification ${type} ${isVisible ? 'show' : ''}`}>
      <div className="notification-content">
        <i className={getIcon()}></i>
        <span>{message}</span>
      </div>
      <button className="notification-close" onClick={onClose}>
        <i className="fas fa-times"></i>
      </button>
    </div>
  );
}
