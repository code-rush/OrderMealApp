using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace OrderMeal
{
    public partial class SelectMealOptions : ContentPage
    {
        public SelectMealOptions()
        {
            InitializeComponent();

            getimg();
        }

        async void Handle_Clicked(object sender, System.EventArgs e)
        {
            if (string.IsNullOrEmpty(optionOne.Text) && string.IsNullOrEmpty(optionTwo.Text)) 
            {
                await DisplayAlert("Order Error", "Please make an order to continue", "Continue");
            }
            else
            {
                var secondPage = new CheckOutPage(optionOne.Text, optionTwo.Text);
                await Navigation.PushAsync(secondPage);
            }
        }

        //leaving this function here for the meal photo GET request
        async Task getimg()
        {
            string uri = createUrl();


            var client = new HttpClient();
            System.Diagnostics.Debug.Print("about to make get request");
            //string uri = "https://s3-us-west-2.amazonaws.com/ordermealapp/" + date;
            Console.WriteLine(uri);
            Stream stream = await client.GetStreamAsync(uri);

            Image img = new Image();
            img.Source = ImageSource.FromStream(() => stream);

            mealPhoto.Source = img.Source;
        }
        public string createUrl()
        {
            DateTime dateTime = DateTime.UtcNow.Date;
            var today = dateTime.ToString("yyyyMMdd");

            string url = "https://s3-us-west-2.amazonaws.com/ordermealapp/" + today;
            return url;
        }
    }
}
