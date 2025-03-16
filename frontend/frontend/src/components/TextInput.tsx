import styled from "@emotion/styled";
import { motion } from "framer-motion";
import { useState } from "react";

interface TextInputProps {
	placeholder?: string;
	onSubmit: (text: string) => void;
	loading?: boolean;
}

const InputContainer = styled.div`
  position: relative;
  width: 100%;
  padding: 1.5rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  backdrop-filter: blur(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const SendButton = styled(motion.button)`
  position: absolute;
  right: 2rem;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 12px;
  padding: 0.5rem 1rem;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const LoadingSpinner = styled(motion.div)`
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
`;

const TextInput: React.FC<TextInputProps> = ({
	placeholder = "Ask a question... / Задайте въпрос...",
	onSubmit,
	loading = false,
}) => {
	const [text, setText] = useState("");

	const handleSubmit = () => {
		if (text.trim() && !loading) {
			onSubmit(text);
			setText("");
		}
	};

	const handleKeyDown = (e: React.KeyboardEvent) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit();
		}
	};

	return (
		<InputContainer>
			<Input
				placeholder={placeholder}
				value={text}
				onChange={(e) => setText(e.target.value)}
				onKeyDown={handleKeyDown}
				disabled={loading}
			/>
			<SendButton
				onClick={handleSubmit}
				disabled={!text.trim() || loading}
				whileHover={{ scale: 1.05 }}
				whileTap={{ scale: 0.95 }}
			>
				{loading ? (
					<LoadingSpinner
						animate={{ rotate: 360 }}
						transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
					/>
				) : (
					"Send / Изпрати"
				)}
			</SendButton>
		</InputContainer>
	);
};

export default TextInput;