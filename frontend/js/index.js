    // Initialize AOS with faster animations
    AOS.init({
      once: true,
      easing: 'ease-out-cubic',
      duration: 800,
      offset: 50,
      delay: 0,
    });
    
    // Create stars background
    function createStars() {
      const starsContainer = document.getElementById('stars');
      const starsCount = 150;
      
      for (let i = 0; i < starsCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        const size = Math.random() * 3;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        
        star.style.animationDuration = `${Math.random() * 3 + 2}s`;
        star.style.animationDelay = `${Math.random() * 2}s`;
        
        starsContainer.appendChild(star);
      }
    }
    
    createStars();