import styled from '@emotion/styled';
import { motion } from 'framer-motion';

interface UserQueryProps {
  query: string;
}

const QueryContainer = styled(motion.div)`
  margin-bottom: 1.5rem;
  margin-left: auto;
  margin-right: 2rem;
  max-width: 80%;
  text-align: right;
`;

const QueryCard = styled.div`
  background: rgba(108, 99, 255, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 1rem 1.5rem;
  display: inline-block;
  text-align: left;
`;

const QueryText = styled.p`
  margin: 0;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  line-height: 1.5;
`;

const UserLabel = styled.div`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
  margin-top: 0.5rem;
  font-style: italic;
`;

const UserQuery: React.FC<UserQueryProps> = ({ query }) => {
  return (
    <QueryContainer
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <QueryCard>
        <QueryText>{query}</QueryText>
      </QueryCard>
      <UserLabel>You</UserLabel>
    </QueryContainer>
  );
};

export default UserQuery;