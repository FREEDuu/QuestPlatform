import axios from 'axios';

const baseURL = 'http://localhost:8000/'; 

export const getUsers = async () => {
  try {
    const response = await axios.get(`${baseURL}users/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const getUser = async (userId) => {
  try {
    const response = await axios.get(`${baseURL}users/${userId}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const response = await axios.post(`${baseURL}users/`, userData);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error; 
  }
};

export const updateUser = async (userId, updatedData) => {
  try {
    const response = await axios.put(`${baseURL}users/${userId}/`, updatedData);
    return response.data;
  } catch (error) {
    console.error('Error updating user:', error);
    throw error; 
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await axios.delete(`${baseURL}users/${userId}/`);
    return response.data; 
  } catch (error) {
    console.error('Error deleting user:', error);
    throw error; 
  }
};
