#![no_std]
use soroban_sdk::{contract, contractimpl, Env, String};

const CID : &str = "";

#[contract]
pub struct ChatContract;

#[contractimpl]
impl ChatContract {
    pub fn store_cid(env: Env, cid: String) -> String {
        env.storage().instance().set(&CID, &cid);
        // env.storage().instance().bump(100);
        cid
    }

    // pub fn get_cid(env: Env) -> String{
    //     let cid: &str = env.storage().instance().get(&CID);
    //     cid
    // }
}
