import React,{useEffect, useState} from "react";
import axios from 'axios';

function Profile (){
    const [user, setUser] = userState(null);
    useEffect(() => {
        const fetchProfile = async () =>{
            try{
                const token = localStorage;
                const res = await axios.get('');
                    headers: {Authorization: 'Bearer ${token}' }
    });
        }
    )
    return (
        <div>
        <h2>Profile</h2>
        <p>Welcome</p>
        <p> {User.fullName}</p>
        <p>{User.email}</p>
        </div>
    );
}
export default Profile