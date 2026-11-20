import React, {userState} from 'react';
import axios from 'axios';
import{ useNavigate} from '<react-router-dom';
import{response } from 'express';

function Login(){
    const navigate = useNavigate({
    const [formData, setFormData] = userState();
    email: '',
    password: '',
});
const handleChange = async e => {
    e.preventDefault();
    try{
        const res=await axios.post('http:localhost:5000/api/login',formData);
        localStorage.setItem('token,res.data.token');
        alert('Login Successful');
        navigate('/profile');
    }
    catch(err) {
        alert(err.response?.data?.message || 'Login failed');
    }
};


    return (
    <form> 
        <h2> Login</h2>
        <input name = "email" placeholder="email" onChange={handleChange} required /> 
        <input name =" password" placeholder="password" type="password" onChange={handleChange} required />
        <button type="submit">Login</button>


        </form>
    );
}
export default Login