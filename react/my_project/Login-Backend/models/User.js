import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
    fullname:{
        type:String,
        require:true,
        unique: true,
    },
    email : {
        type: String,
        required:true,
        unique: true,
    }
});
export default mongoose.model('user', userSchema);
