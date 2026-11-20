import React, {userState} from 'react';
import axios from 'axios';
import{ useNavigate} from '<react-router-dom';
import Register from '../Register';

function Register(){
    const navigate = useNavigate();
    const [formData, setFormData] = userState({
    email: '',
    password: '',
});
const handleChange = async e => {
    setFormData({...formData, [e.target.name]: e.target.value});

};
const handleSubmit = async e => {
    e.preventDefault();
    try{
        await axios.post('http:localhost:5000/api/register', formData);
        alert('Registeration successful');
        navigate('/login');
    } catch (err) {
     alert(err.response?.data?.message || 'Registration failed');

    }
};


    return (
    <form onSubmit={handleSubmit}> 
        <h2> Register</h2>
        <input name = "fullName" placeholder="Full Name" onChange={handleChange} required />
        <input name = "email" placeholder="email" onChange={handleChange} required /> 
        <input name =" password" placeholder="password" type="password" onChange={handleChange} required />
        <button type="submit">Register</button>


        </form>
    );
}
export default Register