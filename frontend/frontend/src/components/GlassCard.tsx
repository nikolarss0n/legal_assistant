import styled from '@emotion/styled';
import { motion } from 'framer-motion';

interface GlassCardProps {
  width?: string;
  height?: string;
  padding?: string;
  children: React.ReactNode;
  onClick?: () => void;
}

const GlassCardContainer = styled(motion.div)<Omit<GlassCardProps, 'children'>>`
  width: ${props => props.width || 'auto'};
  height: ${props => props.height || 'auto'};
  padding: ${props => props.padding || '1.5rem'};
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  color: white;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
  }
`;

const GlassCard: React.FC<GlassCardProps> = ({ 
  children, 
  width, 
  height, 
  padding,
  onClick
}) => {
  return (
    <GlassCardContainer 
      width={width} 
      height={height} 
      padding={padding}
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </GlassCardContainer>
  );
};

export default GlassCard;